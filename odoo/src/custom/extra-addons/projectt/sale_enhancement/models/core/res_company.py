from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    pallet_weight = fields.Float(string="Pallet weight", required=False)
