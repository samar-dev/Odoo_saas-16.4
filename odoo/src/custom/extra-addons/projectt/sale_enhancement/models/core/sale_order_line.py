from markupsafe import Markup

from odoo import fields, models, api, _
from odoo.tools import float_compare


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    net_weight = fields.Float(
        string=_("Net weight"), compute="_compute_weight", store=True
    )
    gross_weight = fields.Float(
        string=_("Gross weight"), compute="_compute_weight", store=True
    )
    nbr_pallet = fields.Float(
        string=_("Pallet number"), compute="_compute_nbr_pallet", store=True
    )
    x_nbr_pallet = fields.Float(string="Nbr palette M")
    x_container_number = fields.Char(string="Container number")

    duplicate = fields.Boolean(string=_("Duplicate"), default=False)

    @api.depends(
        "product_id",
        "product_uom_qty",
        "product_packaging_id",
        "product_packaging_qty",
        "order_id.x_flexitank_number",
        "x_nbr_pallet",
    )
    def _compute_weight(self):
        for line in self:
            if line.nbr_pallet != line.x_nbr_pallet and line.x_nbr_pallet > 0:
                line.net_weight = line.product_id.weight * line.product_uom_qty
                line.gross_weight = (
                        (
                                line.product_packaging_id.package_type_id.base_weight
                                * line.product_packaging_qty
                        )
                        + line.x_nbr_pallet * 20
                        + (float(self.order_id.x_flexitank_number) * 130)
                )
            else:
                line.net_weight = line.product_id.weight * line.product_uom_qty
                line.gross_weight = (
                        (
                                line.product_packaging_id.package_type_id.base_weight
                                * line.product_packaging_qty
                        )
                        + line.nbr_pallet * 20
                        + (float(self.order_id.x_flexitank_number) * 130)
                )

    @api.depends("product_id", "product_packaging_id", "product_packaging_qty")
    def _compute_nbr_pallet(self):
        for line in self:
            line.nbr_pallet = (
                line.product_packaging_qty / line.product_packaging_id.pallet
                if line.product_packaging_id.pallet
                else 0.0
            )

    def _update_line_price(self, values):
        orders = self.mapped("order_id")
        for order in orders:
            order_lines = self.filtered(lambda x: x.order_id == order)
            msg = Markup("<b>%s</b><ul>") % _("The unit price has been updated.")
            for line in order_lines:
                if (
                        "product_id" in values
                        and values["product_id"] != line.product_id.id
                ):
                    # tracking is meaningless if the product is changed as well.
                    continue
                msg += Markup("<li> %s: <br/>") % line.product_id.display_name
                msg += _(
                    "Price unit: %(old_qty)s -> %(new_qty)s",
                    old_qty=line.price_unit,
                    new_qty=values["price_unit"],
                ) + Markup("<br/>")
            msg += Markup("</ul>")
            order.message_post(body=msg)

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        for line in lines:
            if line.product_id and line.state != "sale":
                msg = _("Extra line with %s", line.product_id.display_name)
                line.order_id.message_post(body=msg)
        return lines

    def write(self, values):
        if "product_uom_qty" in values:
            precision = self.env["decimal.precision"].precision_get(
                "Product Unit of Measure"
            )
            self.filtered(
                lambda r: r.state != "sale"
                          and float_compare(
                    r.product_uom_qty,
                    values["product_uom_qty"],
                    precision_digits=precision,
                )
                          != 0
            )._update_line_quantity(values)
        if "price_unit" in values:
            precision = self.env["decimal.precision"].precision_get(
                "Product Unit of Measure"
            )
            self.filtered(
                lambda r: float_compare(
                    r.price_unit,
                    values["price_unit"],
                    precision_digits=precision,
                )
                          != 0
            )._update_line_price(values)

        result = super().write(values)
        return result

    def unlink(self):
        for line in self:
            if line.state != "sale":
                msg = _("Removed line with %s", line.product_id.display_name)
                line.order_id.message_post(body=msg)
        return super().unlink()

    def _compute_product_packaging_id(self):
        res = super(SaleOrderLine, self)._compute_product_packaging_id()
        for line in self:
            if line.product_id and line.product_uom_qty and line.product_uom:
                suggested_packaging = line.product_id.packaging_ids.filtered(
                    lambda p: p.sales
                              and (p.product_id.company_id <= p.company_id <= line.company_id)
                )
                line.product_packaging_id = (
                    suggested_packaging[0]
                    if suggested_packaging
                    else line.product_packaging_id
                )
        return res
