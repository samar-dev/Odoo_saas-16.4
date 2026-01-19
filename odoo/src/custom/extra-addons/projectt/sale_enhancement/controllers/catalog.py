from odoo.http import request
from odoo.addons.sale.controllers.catalog import CatalogController
from odoo.tools import groupby


class CatalogController(CatalogController):
    def sale_product_catalog_update_sale_order_line_info(
        self, order_id, product_id, quantity
    ):
        print(product_id)
        price_unit = super().sale_product_catalog_update_sale_order_line_info(
            order_id, product_id, quantity
        )
        order = request.env["sale.order"].browse(order_id)
        if order:
            sol = request.env["sale.order.line"].search(
                [
                    ("order_id", "=", order_id),
                    ("product_id", "=", product_id),
                ]
            )
            if sol and sol.product_packaging_id:
                sol.product_packaging_qty = quantity

        return price_unit

    def sale_product_catalog_get_sale_order_lines_info(self, order_id, product_ids):
        sale_order_line_info = super().sale_product_catalog_get_sale_order_lines_info(
            order_id, product_ids
        )
        order = request.env["sale.order"].browse(order_id)
        for product, lines in groupby(
            order.order_line.filtered(lambda line: not line.display_type),
            lambda line: line.product_id,
        ):
            if not ((len(lines) > 1) or lines[0].product_uom != product.uom_id):
                line = lines[0]
                if product.id in sale_order_line_info.keys():
                    sale_order_line_info[product.id]["quantity"] = (
                        line.product_packaging_qty
                        if line.product_packaging_id
                        else line.product_uom_qty
                    )
        return sale_order_line_info
