from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tests.common import Form


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    with_withholding = fields.Boolean(string="Avec retenue", default=False)
    withholding_tax_id = fields.Many2one(
        string="Retenue", comodel_name="withholding.tax"
    )
    subtract_tax_stamp = fields.Boolean(
        string="Retrancher timbre fiscal", default=False
    )
    withholding_amount = fields.Monetary(
        string="Montant Retenue",
        currency_field="currency_id",
        compute="_compute_withholding_amount",
        store=True,
        readonly=False,
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

    @api.depends("amount", "withholding_tax_id", "subtract_tax_stamp")
    def _compute_withholding_amount(self):
        for record in self:
            tax_amount = record._get_tax_amount()
            amount = record.amount
            if record.subtract_tax_stamp:
                amount -= tax_amount
            record.withholding_amount = record.withholding_tax_id.percentage * amount

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

    def _get_tax_amount(self):
        tax_amount = 0
        if self._is_tax_stamp_installed():
            product_id = self.env["product.product"].search(
                [
                    ("is_tax_stamp", "=", True),
                    ("company_id", "in", [False, self.env.company.id]),
                ],
                limit=1,
            )
            # if we try to pay more than one invoice  and subtract the tax stamp amount
            # we check how many stamp lines we have in total
            # if we got 3 invoices but only two invoices with tax stamp,
            # we multiply by two
            tax_amount = product_id.taxes_id.amount * len(
                self.line_ids.move_id.line_ids.filtered(
                    lambda line: line.product_id.is_tax_stamp
                )
            )
        return tax_amount

    def _get_custom_fields(self):
        res = super(AccountPaymentRegister, self)._get_custom_fields()
        res.update(
            {
                "withholding_tax_id": self.withholding_tax_id.id,
                "with_withholding": self.with_withholding,
                "subtract_tax_stamp": self.subtract_tax_stamp,
                "withholding_amount": self.withholding_amount,
            }
        )
        if self.with_withholding:
            res.update(
                {
                    "amount": self.amount - self.withholding_amount,
                }
            )
        return res

    def _create_payments(self):
        res = super(
            AccountPaymentRegister, self.with_context(created_from_wizard=True)
        )._create_payments()
        for payment in res.filtered_domain([("with_withholding", "=", True)]):
            with Form(self.env["account.payment.register"]) as form:
                form.journal_id = payment.withholding_tax_id.journal_id
                form.withholding_tax_id = payment.withholding_tax_id
                form.communication = payment.name
                form.payment_date = self.payment_date
            record = form.save()
            record.amount = payment.withholding_amount
            # it will return the action to be opened
            # inside that action we have a res_id contains the id of the new payment
            # also it can contain a domain with the ids of the payment
            # if it is more than one
            # if dont_redirect_to_payments is True the action won't be returned
            action = record.with_context(
                dont_redirect_to_payments=False, original_payment=payment.id
            ).action_create_payments()
            res_id = action.get("res_id", 0)

            withholding_payment_id = self.env["account.payment"].browse(res_id)
            payment.withholding_payment_id = withholding_payment_id

        return res

    def _create_payment_vals_from_wizard(self, batch_result):
        res = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard(
            batch_result
        )
        # pass our customized fields from the wizard to account_payment
        res.update(self._get_custom_fields())
        return res

    def _create_payment_vals_from_batch(self, batch_result):
        res = super(AccountPaymentRegister, self)._create_payment_vals_from_batch(
            batch_result
        )
        # pass our customized fields from the wizard to account_payment
        res.update(self._get_custom_fields())
        return res
