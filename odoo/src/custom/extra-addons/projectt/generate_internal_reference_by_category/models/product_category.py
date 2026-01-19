from odoo import models, fields, api


class ProductCategory(models.Model):
    _inherit = "product.category"

    sequence_by_category = fields.Boolean(string="Sequence by category", default=False)
    sequence_id = fields.Many2one(comodel_name="ir.sequence", string="Sequence")

    @api.onchange("sequence_by_category")
    def create_ir_sequence(self):
        if self.sequence_by_category and not self.sequence_id:
            sequence_id = self.env["ir.sequence"].sudo().create(
                {
                    "name": "%s Category ref" % self.name,
                    "code": "ir_sequence_%s" % self.name.lower(),
                    "prefix": self.name.upper(),
                    "active": True,
                    "padding": 4,
                }
            )
            self.write({"sequence_id": sequence_id})
