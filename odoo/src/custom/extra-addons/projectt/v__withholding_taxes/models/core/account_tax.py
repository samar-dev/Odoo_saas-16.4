from odoo import fields, models


class AccountTax(models.Model):
    _inherit = "account.tax"

    is_withholding_tax = fields.Boolean(string="Retenue à la source", default=False)
