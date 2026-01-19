from odoo import models, fields


class ProductProduct(models.Model):
    _inherit = "product.product"

    etiquette_ids = fields.Many2many(
        comodel_name="product.etiquette",
        relation="product_product_etiquette_rel",
        column1="product_id",
        column2="etiquette_id",
        string="Etiquettes Affichage",
    )
