from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    x_use_risk_limit = fields.Boolean(string="Blocage par risque")
