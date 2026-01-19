from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    x_block_unpaid_customer = fields.Boolean(
        string="Bloquer les clients impayés",
        related="company_id.x_block_unpaid_customer",
        readonly=False,
    )
