from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    x_customer_blocked = fields.Boolean(string="Customer Blocked")

    is_printable = fields.Boolean(string="Imprimer" , default=True)

    delivered_pallets = fields.Float(
        string="Palettes livrées", compute="_compute_pallet_balances", store=True
    )
    initial_pallets = fields.Float(
        string="Solde Depart", store=True
    )
    returned_pallets = fields.Float(
        string="Palettes retournées", compute="_compute_pallet_balances", store=True
    )
    pallet_balance = fields.Float(
        string="Solde palettes", compute="_compute_pallet_balances", store=True
    )

    @api.depends("delivered_pallets", "returned_pallets")
    def _compute_pallet_balances(self):
        pallet_products = (
            self.env["product.product"]
            .search([("product_tmpl_id.is_pallet", "=", True)])
            .ids
        )
        for partner in self:
            pickings = self.env["stock.picking"].search(
                [
                    ("partner_id", "=", partner.id),
                    ("state", "=", "done"),
                    ("picking_type_id.code", "in", ["outgoing", "incoming"]),
                ]
            )
            delivered_qty = returned_qty = 0.0
            for picking in pickings:
                for move in picking.move_ids:
                    if move.product_id.id in pallet_products:
                        if picking.picking_type_id.code == "outgoing":
                            delivered_qty += move.quantity_done
                        elif picking.picking_type_id.code == "incoming":
                            returned_qty += move.quantity_done
            partner.delivered_pallets = delivered_qty
            partner.returned_pallets = returned_qty
            partner.pallet_balance = delivered_qty - returned_qty + partner.initial_pallets

    def action_recompute_pallets(self):
        for partner in self:
            partner._compute_pallet_balances()

    def action_set_printable(self):
        for partner in self:
            partner.is_printable = True
