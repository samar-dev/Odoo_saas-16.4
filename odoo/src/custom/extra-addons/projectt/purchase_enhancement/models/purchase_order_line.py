from odoo import fields, models, api


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.onchange("product_id")
    def _set_product_packaging(self):
        self.product_packaging_id = (fields.first(
            self.product_packaging_id.search(
                [("purchase", "=", True), ("product_id", "=", self.product_id.id)]
            )
        ))

    @api.onchange("product_packaging_id")
    def _set_product_packaging_qty(self):
        self.product_packaging_qty = 1.0
