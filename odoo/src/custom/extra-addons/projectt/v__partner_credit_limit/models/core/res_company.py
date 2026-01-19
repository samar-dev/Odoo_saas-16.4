from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    x_account_use_credit_limit = fields.Boolean(string="Blocage par encours")
