from odoo import _, fields, models


class AccountFactoringCommission(models.Model):
    _name = "account.factoring.commission"
    account_factoring_id = fields.Many2one(comodel_name="account.factoring")
    name = fields.Char(string=_("Name"), required=True, readonly=True)
    label = fields.Char(string=_("Label"), required=True)
    account_id = fields.Many2one(
        string=_("Account"),
        comodel_name="account.account",
        required=True,
    )
    value_type = fields.Selection(
        string=_("Value Type"),
        selection=[("amount", _("Amount")), ("percentage", _("Percentage"))],
        required=True,
        default="amount",
    )
    value = fields.Float(string=_("Value"), required=True, default=0)
