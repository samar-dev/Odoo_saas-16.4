from odoo import models, fields, api


class ProductCategory(models.Model):
    _inherit = "product.category"

    other_operation = fields.Boolean(string="Other Operation")

    # Many2one field linking to stock.picking.type model
    operation = fields.Many2one(
        comodel_name="stock.picking.type",  # This is the model you are referencing
        string="Operation Type",
    )
