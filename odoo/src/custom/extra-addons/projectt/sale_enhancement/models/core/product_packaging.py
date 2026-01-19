from odoo import fields, models, _


class ProductPackaging(models.Model):
    _inherit = "product.packaging"

    pallet = fields.Float(string=_("Pallet"))
