from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    x_verify_payment = fields.Boolean(string="Vérification du paiement")
