from odoo import models, fields


class ProductEtiquette(models.Model):
    _name = "product.etiquette"
    _description = "Product Etiquette"

    name = fields.Char(required=True)
