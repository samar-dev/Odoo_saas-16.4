from odoo import _, fields, models


class AccountCommissionLine(models.Model):
    _name = "account.commission.line"
    _order = "sequence asc"

    account_commission_id = fields.Many2one(comodel_name="account.commission")
    sequence = fields.Integer(default=1)
    name = fields.Char(string=_("Name"), required=True)
    label = fields.Char(string=_("Label"), required=True)
    value_type = fields.Selection(
        string=_("Value Type"),
        selection=[("amount", _("Amount")), ("percentage", _("Percentage"))],
        required=True,
        default="variable",
    )
    value = fields.Float(string=_("Value"), default=0, required=True)
    account_id = fields.Many2one(
        string=_("Account"), comodel_name="account.account", required=True
    )
