from odoo import fields, models, api, _


class StockMove(models.Model):
    _inherit = "stock.move"

    net_weight = fields.Float(
        string=_("Net weight"), compute="_compute_weight", store=True
    )
    gross_weight = fields.Float(
        string=_("Gross weight"), compute="_compute_weight", store=True
    )
    nbr_pallet = fields.Float(
        string=_("Pallet number"), compute="_compute_nbr_pallet", store=True
    )

    @api.depends(
        "product_id",
        "quantity_done",
        "product_packaging_id",
    )
    def _compute_weight(self):
        for line in self:
            line.net_weight = line.product_id.weight * line.quantity_done
            line.gross_weight = (
                (
                    line.product_packaging_id.package_type_id.base_weight
                    * line.quantity_done
                    / line.product_packaging_id.qty
                )
                if line.product_packaging_id.qty
                else 0.0
            )

    @api.depends("product_id", "quantity_done", "product_packaging_id")
    def _compute_nbr_pallet(self):
        for line in self:
            line.nbr_pallet = (
                (line.quantity_done / line.product_packaging_id.qty)
                / line.product_packaging_id.pallet
                if line.product_packaging_id.pallet
                else 0.0
            )
