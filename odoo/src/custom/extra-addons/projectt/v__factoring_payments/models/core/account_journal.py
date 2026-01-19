from odoo import _, fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    x_type = fields.Selection(selection_add=[("factoring", "Factoring")])
    journal_factoring_line_ids = fields.One2many(
        comodel_name="account.journal.factoring.line", inverse_name="journal_id"
    )
