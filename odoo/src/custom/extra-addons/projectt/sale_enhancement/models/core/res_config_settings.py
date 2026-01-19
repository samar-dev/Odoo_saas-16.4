from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    pallet_weight = fields.Float(string="Pallet weight", related="company_id.pallet_weight", readonly=False)
