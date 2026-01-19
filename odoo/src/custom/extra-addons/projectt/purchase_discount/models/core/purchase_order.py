from odoo import models, api


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.model
    def _prepare_sale_order_line_data(self, line, company):
        res = super(PurchaseOrder, self)._prepare_sale_order_line_data(line, company)
        res["discount"] = line.pol_discount
        return res
