from odoo import _, fields, models


class AccountPaymentCommission(models.Model):
    _name = "account.payment.commission"

    payment_id = fields.Many2one(comodel_name="account.payment")
    name = fields.Char(string=_("Name"), required=True, readonly=True)
    label = fields.Char(string=_("Label"), required=True, readonly=True)
    value_type = fields.Selection(
        string=_("Value Type"),
        selection=[("amount", _("Amount")), ("percentage", _("Percentage"))],
        required=True,
        default="variable",
    )
    value = fields.Float(string=_("Value"), default=0, required=True)
    account_id = fields.Many2one(
        string=_("Account"),
        comodel_name="account.account",
        required=True,
        readonly=True,
    )
