from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    purchase_id = fields.Many2one("purchase.order", "Purchase Order")

    def create_purchase(self):
        context = {"default_sale_id": self.id}
        return {
            "type": "ir.actions.act_window",
            "name": "Update Purchase Quantity",
            "view_mode": "form",
            "target": "new",
            "res_model": "wizard.create.purchase",
            "context": context,
        }


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    sale_id = fields.Many2one("sale.order", "Sale Order")
