from odoo import api, fields, models
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    with_withholding = fields.Boolean(string="Avec retenue", default=False)
    withholding_tax_id = fields.Many2one(
        string="Retenue",
        comodel_name="withholding.tax",
    )
    subtract_tax_stamp = fields.Boolean(
        string="Retrancher timbre fiscal", default=False
    )
    withholding_amount = fields.Monetary(
        string="Montant Retenue",
        currency_field="currency_id",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    withholding_payment_id = fields.Many2one(
        string="Retenue de paiement",
        comodel_name="account.payment",
        readonly=True,
    )
    is_withholding = fields.Boolean(compute="_compute_is_withholding", store=True)

    @api.depends("journal_id")
    def _compute_is_withholding(self):
        for record in self:
            record.is_withholding = record.journal_id.x_type == "withholding"

    def _is_tax_stamp_installed(self):
        ir_module_obj = self.env["ir.module.module"].sudo()
        module_id = ir_module_obj.search_count(
            [
                ("name", "=", "v__tax_stamp"),
                ("state", "=", "installed"),
            ]
        )
        return module_id

    @api.onchange("subtract_tax_stamp")
    def _onchange_subtract_tax_stamp(self):
        message = (
            "Installez le module suivant v__tax_stamp"
            " pour utiliser cette fonctionnalité"
        )
        if self.subtract_tax_stamp and not self._is_tax_stamp_installed():
            raise UserError(message)

    @api.onchange("journal_id", "with_withholding")
    def _set_default_withholding_tax_id(self):
        if self.with_withholding or self.journal_id.x_type == "withholding":
            self.withholding_tax_id = self.env["withholding.tax"].search(
                [
                    ("company_id", "=", self.env.company.id),
                    ("type", "=", self.payment_type),
                ],
                limit=1,
            )

    @api.onchange("amount", "withholding_tax_id", "subtract_tax_stamp")
    def _compute_withholding_amount(self):
        tax_amount = 0
        if self._is_tax_stamp_installed():
            product_id = self.env["product.product"].search(
                [
                    ("is_tax_stamp", "=", True),
                    ("company_id", "in", [False, self.env.company.id]),
                ],
                limit=1,
            )
            tax_amount = product_id.taxes_id.amount
        amount = self.amount
        if self.subtract_tax_stamp:
            amount -= tax_amount
        self.withholding_amount = self.withholding_tax_id.percentage * amount

    def action_print_withholding_certificate(self):
        self.ensure_one()
        action_id = self.env.ref(
            "v__withholding_taxes.account_payment_withholding_certificate_action"
        )
        return action_id.report_action(self)

    def _get_valid_liquidity_accounts(self):
        # as long as we are not using the default account of the withholding journal
        # we pass its account to the liquidity accounts to avoid exceptions
        res = super(AccountPayment, self)._get_valid_liquidity_accounts()
        if isinstance(res, tuple):
            res = list(res)
            res.append(self.withholding_tax_id.account_id)
            res = tuple(res)
        else:
            res |= self.withholding_tax_id.account_id
        return res

    @api.depends(
        "move_id.line_ids.amount_residual",
        "move_id.line_ids.amount_residual_currency",
        "move_id.line_ids.account_id",
    )
    def _compute_reconciliation_status(self):
        res = super(AccountPayment, self)._compute_reconciliation_status()
        # after we change the account fo the journal item
        # odoo doesn't match the payment because the liquidity account was changed by us
        # for that reason if it is not matched we check again using the changed account
        for payment in self:
            if payment.is_withholding and not payment.is_matched:
                (
                    liquidity_lines,
                    counterpart_lines,
                    writeoff_lines,
                ) = payment._seek_for_lines()
                payment.is_matched = (
                    payment.withholding_tax_id.account_id
                    and payment.withholding_tax_id.account_id
                    in liquidity_lines.account_id
                )
        return res

    @api.model_create_multi
    def create(self, vals_list):
        res = super(AccountPayment, self).create(vals_list)
        for payment in res.filtered_domain([("is_withholding", "=", True)]):
            journal_account = payment.journal_id.default_account_id
            line_id = payment.line_ids.filtered(
                lambda line: line.account_id == journal_account
            )
            self.env.cr.execute(
                f"update account_move_line "
                f"set account_id={payment.withholding_tax_id.account_id.id} "
                f"where id={line_id.id}"
            )
        if not res.env.context.get("created_from_wizard") and res.with_withholding:
            res.update(
                {
                    "amount": res.amount - res.withholding_amount,
                }
            )
        return res

    def _get_custom_aml_default_display_name_list(self):
        self.ensure_one()
        if self.is_withholding:
            values = []
            percentage = int(self.withholding_tax_id.percentage * 100)
            values.append(("label", f"R.A.S {percentage}%"))
            if self.partner_id:
                values += [
                    ("sep", " - "),
                    ("partner", self.partner_id.display_name),
                ]
            return values
        return super(AccountPayment, self)._get_custom_aml_default_display_name_list()

    # Create a payment for the withholding tax
    def action_post(self):
        res = super(AccountPayment, self).action_post()
        if not self.env.context.get("created_from_wizard") and self.with_withholding:
            withholding_payment = self.env["account.payment"].create(
                {
                    "partner_id": self.partner_id.id,
                    "amount": self.withholding_amount,
                    "journal_id": self.withholding_tax_id.journal_id.id,
                    "ref": self.name,
                    "withholding_tax_id": self.withholding_tax_id.id,
                    "payment_type": self.payment_type,
                }
            )
            withholding_payment.action_post()
            self.write(
                {
                    "withholding_payment_id": withholding_payment.id,
                }
            )
        return res
