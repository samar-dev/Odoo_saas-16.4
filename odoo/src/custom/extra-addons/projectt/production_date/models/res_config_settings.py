from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    config_production_date = fields.Boolean(
        "Production Dates", config_parameter="production_date.config_production_date"
    )
