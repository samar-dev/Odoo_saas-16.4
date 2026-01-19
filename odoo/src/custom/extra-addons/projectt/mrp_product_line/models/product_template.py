from odoo import _, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_template = fields.Boolean(string=_("Template"), default=False)
