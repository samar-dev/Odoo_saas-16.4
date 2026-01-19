from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    x_product_type = fields.Selection(
        [
            ("immobilisation", "Immobilisation"),
            ("fourniture_divers", "Fourniture Divers"),
        ],
        string="Type Produit",
    )
