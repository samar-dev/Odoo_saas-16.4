from odoo import _, fields, models


class AccountJournalFactoringLine(models.Model):
    _name = "account.journal.factoring.line"
    _order = "sequence asc, name asc"

    name = fields.Char(string=_("Name"), required=True)
    sequence = fields.Integer(default=1)
    company_id = fields.Many2one(
        comodel_name="res.company", related="journal_id.company_id", store=True
    )
    label = fields.Char(string=_("Label"), required=True)
    journal_id = fields.Many2one(comodel_name="account.journal")
    account_id = fields.Many2one(
        string=_("Account"),
        comodel_name="account.account",
        required=True,
        domain="[('company_id', '=', company_id)]",
    )
    value_type = fields.Selection(
        string=_("Value Type"),
        selection=[("amount", _("Amount")), ("percentage", _("Percentage"))],
        required=True,
        default="amount",
    )
    value = fields.Float(string=_("Value"), required=True, default=0)
