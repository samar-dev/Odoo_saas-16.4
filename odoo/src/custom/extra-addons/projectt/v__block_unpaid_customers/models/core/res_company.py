from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    x_block_unpaid_customer = fields.Boolean(string="Bloquer les clients impayés")
