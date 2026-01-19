from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    product_template_variant_value_ids = fields.Many2many(
        domain=[("attribute_line_id.value_count", ">=", 1)]
    )
