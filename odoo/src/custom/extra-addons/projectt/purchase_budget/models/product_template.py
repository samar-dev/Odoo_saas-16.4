from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    produc_qty = fields.Integer(
        string="Theoretical QNT",
    )
