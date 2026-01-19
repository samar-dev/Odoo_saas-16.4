from datetime import date

from odoo import models, fields, api, _, exceptions
from odoo.tests.common import Form


class Picking(models.Model):
    _inherit = "stock.picking"

    vehicle_id = fields.Many2one(comodel_name="fleet.vehicle", string=_("Vehicle"))
    delivery_person_id = fields.Many2one(
        comodel_name="res.partner",
        string=_("Delivery person"),
        domain="[('category_id', '=', 'CHAUFFEUR')]",
    )

    type_of_delivery = fields.Selection(
        [
            ("vrac_c", "Vrac Citerne"),
            ("vrac_f", "Vrac Flexitank"),
            ("conditionner", "Conditionner"),
        ],
        default="vrac_c",
        string="Type de livraison",
    )

    v_delivery_number = fields.Char(string='Réference BL/FAC')

    sum_net_weight = fields.Float(
        string=_("Sum Net weight"), compute="_compute_sum_weight", store=True
    )
    sum_gross_weight = fields.Float(
        string=_("Sum Gross weight"), compute="_compute_sum_weight", store=True
    )

    sum_pallet = fields.Float(
        string=_("Sum Pallet"), compute="_compute_sum_pallet", store=True
    )

    sum_product_packaging_qty = fields.Float(
        string=_("Sum Carton"), compute="_compute_sum_product_packaging_qty", store=True
    )

    container_ids = fields.Many2many(
        "stock.container",
        "stock_picking_container_rel",  # Relation table name
        "picking_id",  # Field for stock.picking in the relation table
        "container_id",  # Field for stock.container in the relation table
        string="Containers",
    )

    @api.depends(
        "move_ids_without_package.net_weight",
        "move_ids_without_package.gross_weight",
    )
    def _compute_sum_weight(self):
        for picking in self:
            pallet_weight = self.env.company.pallet_weight
            picking.sum_net_weight = sum(
                picking.move_ids_without_package.mapped("net_weight")
            )
            picking.sum_gross_weight = sum(
                picking.move_ids_without_package.mapped("gross_weight")
            ) + (pallet_weight * picking.sale_id.x_real_pallet_number)

    @api.depends("move_ids_without_package.nbr_pallet")
    def _compute_sum_pallet(self):
        for picking in self:
            picking.sum_pallet = sum(
                picking.move_ids_without_package.mapped("nbr_pallet")
            )

    @api.depends(
        "move_ids_without_package.quantity_done",
        "move_ids_without_package.product_packaging_id",
    )
    def _compute_sum_product_packaging_qty(self):
        for picking in self:
            picking.sum_product_packaging_qty = sum(
                map(
                    lambda move: (
                        move.quantity_done / move.product_packaging_id.qty
                        if move.product_packaging_id.qty
                        else 0.0
                    ),
                    picking.move_ids_without_package,
                )
            )

    @api.onchange("vehicle_id")
    def _get_delivery_person_id(self):

        self.delivery_person_id = self.vehicle_id.driver_id

    def button_validate(self):
        """
        Override:
            Automatically create unique lot numbers for incoming pickings
            when 'use_create_lots' is enabled.
        """
        if self.use_create_lots and self.picking_type_id.code == "incoming" and self.origin and not self.origin.startswith("SR"):
            for move_line in self.move_line_ids_without_package:
                if move_line.product_id.tracking == "lot" and move_line.product_id.purchase_ok:
                    # Vérifier que le code fournisseur et le code produit existent
                    if not self.partner_id.ref:
                        raise exceptions.UserError(
                            "Le code fournisseur (référence) n’est pas défini pour ce fournisseur.")
                    if not move_line.product_id.default_code:
                        raise exceptions.UserError(
                            f"Le code article n’est pas défini pour le produit {move_line.product_id.name}.")

                    # Get the last lot for this product to determine the next sequence
                    # Filter last lot for the same product AND company
                    last_lot = self.env["stock.lot"].search(
                        [
                            ("product_id", "=", move_line.product_id.id),
                            ("company_id", "=", self.company_id.id)
                        ],
                        order="create_date desc",
                        limit=1
                    )

                    # Determine sequence number
                    last_seq = 0
                    if last_lot and "-" in last_lot.name:
                        parts = last_lot.name.split("-")
                        # Check that there are enough parts and the sequence is numeric
                        if len(parts) >= 4 and parts[2].isdigit():
                            last_seq = int(parts[2])
                        else:
                            last_seq = 0
                    # Start from 1 if no previous lot found
                    new_seq = last_seq + 1 if last_seq > 0 else 1

                    # Build unique lot name
                    lot_name = (
                        f"{self.partner_id.ref or ''}-"
                        f"{move_line.product_id.default_code or ''}-"
                        f"{new_seq}-"
                        f"{self.date_done.strftime('%d%m%y') if self.date_done else date.today().strftime('%d%m%y')}"
                    )

                    # Check if a lot with this name already exists for the same product and company
                    existing_lot = self.env["stock.lot"].search(
                        [
                            ("product_id", "=", move_line.product_id.id),
                            ("company_id", "=", self.company_id.id),
                            ("name", "=", lot_name),
                        ],
                        limit=1
                    )

                    if existing_lot:
                        # If exists, use the existing lot
                        lot = existing_lot
                    else:
                        # Otherwise, create a new lot
                        lot = self.env["stock.lot"].create({
                            "name": lot_name,
                            "product_id": move_line.product_id.id,
                            "company_id": self.company_id.id,
                            "product_qty": move_line.qty_done,
                        })

                    # Assign it to the move line
                    move_line.lot_id = lot.id

        # Continue with standard Odoo validation
        return super(Picking, self).button_validate()
