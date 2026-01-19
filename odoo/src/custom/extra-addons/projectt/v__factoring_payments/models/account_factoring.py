from odoo import _, api, fields, models
from odoo.tests.common import Form
from odoo.exceptions import UserError, ValidationError


def _post_change_payments_journal(payment):
    payment.move_id.name = None
    payment.move_id._compute_name()


class AccountFactoring(models.Model):
    _name = "account.factoring"
    _description = "Factoring"
    _order = "name desc, id desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        string=_("Number"),
        required=True,
        default="/",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    state = fields.Selection(
        selection=[
            ("draft", _("Draft")),
            ("pending", _("Pending")),
            ("done", _("Done")),
        ],
        required=True,
        default="draft",
        tracking=True,
    )
    company_id = fields.Many2one(
        string=_("Company"),
        comodel_name="res.company",
        default=lambda self: self.env.company,
    )
    journal_id = fields.Many2one(
        string=_("Journal"),
        comodel_name="account.journal",
        domain="[('x_type', '=', 'factoring'), ('company_id', '=', company_id)]",
        readonly=True,
        states={"draft": [("readonly", False)]},
        tracking=True,
        required=True,
    )
    partner_id = fields.Many2one(
        string=_("Factoring Company"),
        comodel_name="res.partner",
        readonly=True,
        states={"draft": [("readonly", False)]},
        tracking=True,
        required=True,
    )
    date = fields.Date(
        string=_("Date"),
        required=True,
        default=lambda self: fields.date.today(),
        tracking=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    payment_ids = fields.One2many(
        comodel_name="account.payment",
        inverse_name="account_factoring_id",
        readonly=True,
        states={"draft": [("readonly", False)]},
        required=True,
        ondelete="restrict",
    )
    factoring_payment_ids = fields.One2many(
        comodel_name="account.payment", inverse_name="factoring_id"
    )
    factoring_payments_count = fields.Integer(
        compute="_compute_factoring_payments_count"
    )
    account_factoring_commission_ids = fields.One2many(
        comodel_name="account.factoring.commission",
        inverse_name="account_factoring_id",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    factoring_move_id = fields.Many2one(comodel_name="account.move")
    new_amount = fields.Float(string=_("New Amount"))

    @api.depends("factoring_payment_ids")
    def _compute_factoring_payments_count(self):
        for record in self:
            record.factoring_payments_count = len(record.factoring_payment_ids)

    @api.onchange("journal_id")
    def onchange_journal_id(self):
        # empty all lines by default
        self.account_factoring_commission_ids = [(5, 0)]
        values = self.journal_id.journal_factoring_line_ids.mapped(
            lambda line: {
                "name": line.name,
                "label": line.label,
                "account_id": line.account_id.id,
                "value_type": line.value_type,
                "value": line.value,
            }
        )
        self.account_factoring_commission_ids = [(0, 0, value) for value in values]

    def action_open_factoring_move_entry(self):
        self.ensure_one()
        action = {
            "name": self.factoring_move_id.name,
            "view_mode": "form",
            "res_model": "account.move",
            "type": "ir.actions.act_window",
            "res_id": self.factoring_move_id.id,
            "context": {"create": False},
            "target": "self",
        }
        return action

    def action_open_factoring_payments(self):
        self.ensure_one()
        factoring_payments = self.factoring_payment_ids
        action = {
            "name": _("Payments"),
            "view_mode": "tree,form",
            "res_model": "account.payment",
            "type": "ir.actions.act_window",
            "context": {"create": 0},
            "domain": [("id", "in", factoring_payments.ids)],
            "target": "self",
        }
        if len(factoring_payments) == 1:
            action.update(
                {
                    "name": factoring_payments.name,
                    "view_mode": "form",
                    "res_id": factoring_payments.id,
                }
            )
        return action

    def _check_payment_constrains(self):
        self.ensure_one()
        # domain is the inverse of the variable meaning
        payments_must_exists = len(self.payment_ids) == 0
        payment_must_be_posted = self.payment_ids.filtered_domain(
            [("state", "!=", "posted")]
        )
        payment_method_must_be_check = self.payment_ids.filtered_domain(
            [("payment_method_code", "!=", "v-check")]
        )
        payment_must_have_chest_journal = self.payment_ids.filtered_domain(
            [("journal_id.x_type", "!=", 'chest')]
        )
        payment_must_be_inbound = self.payment_ids.filtered_domain(
            [("payment_type", "!=", "inbound")]
        )
        constrains = {
            payments_must_exists: _(
                "You must select at least one single payment to proceed"
            ),
            payment_must_be_posted: _(
                "Payment must be posted before sending it to factoring company."
            ),
            payment_method_must_be_check: _(
                "Payment method is not check, only check is allowed."
            ),
            payment_must_be_inbound: _("Only customer payments are allowed."),
            payment_must_have_chest_journal: _("Payment must be in the chest journal."),
        }
        for error, message in constrains.items():
            if error:
                raise ValidationError(message)

    def _action_change_payments_journal(self):
        self.payment_ids.flush_model()
        for payment in self.payment_ids:
            payment_method_name, payment_type = self._pre_change_payments_journal(
                payment
            )
            payment_method_line_ids = self.journal_id.inbound_payment_method_line_ids
            payment_method_line_ids |= self.journal_id.outbound_payment_method_line_ids
            payment_method_line_id = payment_method_line_ids.filtered_domain(
                [
                    ("name", "=", payment_method_name),
                    ("payment_type", "=", payment_type),
                ]
            )
            payment.invalidate_model()
            payment.payment_method_line_id = payment_method_line_id
            payment.with_context(
                do_not_create_journal_entry=True, do_not_call_wizard=True
            ).action_set_paid()
            _post_change_payments_journal(payment)

    def _pre_change_payments_journal(self, payment):
        payment_method_name = payment.payment_method_name
        payment_type = payment.payment_type
        self.env.cr.execute(
            f"update account_move "
            f"set journal_id={self.journal_id.id}, name=null "
            f"where id={payment.move_id.id}"
        )
        self.env.cr.execute(
            f"update account_move_line "
            f"set journal_id={self.journal_id.id} "
            f"where move_id={payment.move_id.id}"
        )
        return payment_method_name, payment_type

    def action_add_factoring_payment(self):
        self.ensure_one()
        action = {
            "name": _("Factoring Check"),
            "view_mode": "form",
            "res_model": "account.payment",
            "type": "ir.actions.act_window",
            "view_id": self.env.ref(
                "v__payment_methods.view_account_payment_form_without_header"
            ).id,
            "context": {
                "default_partner_id": self.partner_id.id,
                "default_amount": abs(
                    self.new_amount - sum(self.factoring_payment_ids.mapped("amount"))
                ),
                "default_payment_type": "inbound",
                "default_partner_type": "customer",
                "default_move_journal_types": ("bank",),
                "default_ref": self.name,
                "hide_factoring_button": False,
                "hide_replace_button": True,
            },
            "target": "new",
        }
        return action

    def action_send_to_factoring(self):
        self.ensure_one()
        self._check_payment_constrains()
        self._action_change_payments_journal()
        self.payment_ids.invalidate_model()
        total_amount = sum(self.payment_ids.mapped("amount"))
        # debit lines in the customer payments will become credit lines for factoring
        credit_lines = self.payment_ids.move_id.line_ids.filtered_domain(
            [("debit", ">", 0)]
        )
        # prepare debit lines data
        debit_lines_data = []
        debit_amounts = 0
        # null commissions won't be checked or written at all
        for commission_line in self.account_factoring_commission_ids.filtered_domain(
            [("value", ">", 0)]
        ):
            amount = (
                commission_line.value
                if commission_line.value_type == "amount"
                else (total_amount * commission_line.value / 100)
            )
            debit_lines_data.append(
                {
                    "debit": amount,
                    "account_id": commission_line.account_id,
                    "label": commission_line.label,
                }
            )
            debit_amounts += amount
        debit_lines_data.insert(
            0,
            {
                "debit": total_amount - debit_amounts,
                "account_id": self.journal_id.default_account_id,
                "label": f"{self.name} - {self.partner_id.name}",
            },
        )

        with Form(self.with_context(move_type="entry").env["account.move"]) as move:
            move.ref = ",".join(self.payment_ids.mapped("name"))
            move.date = self.date
            # add debit lines first
            for debit_line in debit_lines_data:
                with move.line_ids.new() as line:
                    line.name = debit_line["label"]
                    line.account_id = debit_line["account_id"]
                    line.partner_id = self.partner_id
                    line.debit = debit_line["debit"]
                    line.credit = 0
            # add credit lines
            for credit_line in credit_lines:
                with move.line_ids.new() as line:
                    line.name = credit_line.name
                    line.account_id = credit_line.account_id
                    line.partner_id = self.partner_id
                    line.debit = 0
                    line.credit = credit_line.debit
        factoring_move_id = move.save()
        factoring_move_id.journal_id = self.journal_id
        factoring_move_id.action_post()
        # credit_lines in factoring generated
        # based on the debit lines of the customer payments.
        # so now we will reconcile them
        debit_lines = factoring_move_id.line_ids.filtered_domain([("credit", ">", 0)])
        (debit_lines + credit_lines).reconcile()
        self.write(
            {
                "factoring_move_id": factoring_move_id.id,
                "state": "pending",
                "new_amount": total_amount - debit_amounts,
            }
        )

    @api.model_create_multi
    def create(self, vals_list):
        res = super(AccountFactoring, self).create(vals_list)
        for record in res.filtered_domain([("name", "=", "/")]):
            record.name = self.env["ir.sequence"].next_by_code("account_factoring_seq")
        return res

    @api.ondelete(at_uninstall=False)
    def _on_delete_draft(self):
        for record in self:
            if record.state != "draft":
                raise UserError(
                    _("You can't delete this document because it is not in draft state")
                )
