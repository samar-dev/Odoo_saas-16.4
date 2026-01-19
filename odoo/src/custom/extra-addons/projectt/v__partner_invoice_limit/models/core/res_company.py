from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    x_use_invoice_limit = fields.Boolean(string="Blocage par facture")
