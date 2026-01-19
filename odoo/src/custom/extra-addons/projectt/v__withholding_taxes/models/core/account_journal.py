from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    x_type = fields.Selection(selection_add=[("withholding", "Retenue à la source")])
