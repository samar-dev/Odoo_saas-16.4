from odoo import models, fields, api


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    max_purchase_price = fields.Float(
        string="Max Purchase Price",
        compute="_compute_max_purchase_price",
        store=True,
        help="Récupéré depuis le prix cible du produit lié (Target Price).",
    )

    @api.depends("product_id", "product_id.product_tmpl_id.target_price")
    def _compute_max_purchase_price(self):
        for line in self:
            if line.product_id and line.product_id.product_tmpl_id:
                line.max_purchase_price = line.product_id.product_tmpl_id.target_price
            else:
                line.max_purchase_price = 0.0
