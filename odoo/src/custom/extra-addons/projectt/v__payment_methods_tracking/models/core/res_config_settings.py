from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    x_verify_payment = fields.Boolean(
        string="Vérification du paiement",
        related="company_id.x_verify_payment",
        readonly=False,
    )
