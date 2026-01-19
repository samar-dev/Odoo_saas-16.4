from odoo import models, api, fields


class StockPicking(models.Model):
    _inherit = "stock.picking"

    delivered_pallets = fields.Float(
        string="Palettes livrées", compute="_compute_pallet_values", store=True
    )
    returned_pallets = fields.Float(
        string="Palettes retournées", compute="_compute_pallet_values", store=True
    )
    pallet_balance = fields.Float(
        string="Solde palettes", compute="_compute_pallet_values", store=True
    )
    historical_delivered_pallets = fields.Float(
        string="Cumul livré avant", compute="_compute_pallet_values", store=True
    )
    historical_returned_pallets = fields.Float(
        string="Cumul retourné avant", compute="_compute_pallet_values", store=True
    )
    historical_pallet_balance = fields.Float(
        string="Solde avant", compute="_compute_pallet_values", store=True
    )

    @api.depends("move_ids.quantity_done", "state", "partner_id")
    def _compute_pallet_values(self):
        pallet_products = set(
            self.env["product.product"]
            .search([("product_tmpl_id.is_pallet", "=", True)])
            .ids
        )

        for picking in self:
            if picking.state != "done" or not picking.partner_id:
                picking.delivered_pallets = 0.0
                picking.returned_pallets = 0.0
                picking.pallet_balance = 0.0
                picking.historical_delivered_pallets = 0.0
                picking.historical_returned_pallets = 0.0
                picking.historical_pallet_balance = 0.0
                continue

            qty = sum(
                move.quantity_done
                for move in picking.move_ids
                if move.product_id.id in pallet_products
            )

            is_out = picking.picking_type_id.code == "outgoing"
            is_in = picking.picking_type_id.code == "incoming"

            picking.delivered_pallets = qty if is_out else 0.0
            picking.returned_pallets = qty if is_in else 0.0
            picking.pallet_balance = qty if is_out else -qty if is_in else 0.0

            prev_pickings = self.env["stock.picking"].search(
                [
                    ("partner_id", "=", picking.partner_id.id),
                    ("state", "=", "done"),
                    ("id", "<", picking.id),
                    ("picking_type_id.code", "in", ["outgoing", "incoming"]),
                ]
            )

            hist_delivered = hist_returned = 0.0
            for prev in prev_pickings:
                is_prev_out = prev.picking_type_id.code == "outgoing"
                is_prev_in = prev.picking_type_id.code == "incoming"
                for move in prev.move_ids:
                    if move.product_id.id in pallet_products:
                        if is_prev_out:
                            hist_delivered += move.quantity_done
                        elif is_prev_in:
                            hist_returned += move.quantity_done

            picking.historical_delivered_pallets = hist_delivered
            picking.historical_returned_pallets = hist_returned
            picking.historical_pallet_balance = hist_delivered - hist_returned

            picking.partner_id.delivered_pallets = picking.historical_delivered_pallets
            picking.partner_id.returned_pallets = picking.historical_returned_pallets
            picking.partner_id.pallet_balance = picking.historical_pallet_balance
