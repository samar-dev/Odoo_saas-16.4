from datetime import date

from odoo import models, fields, api, _, exceptions


class Picking(models.Model):
    _inherit = "stock.picking"

    def action_generate_lots(self):
        """
        Custom Button:
            Automatically create unique lot numbers for incoming pickings
            when 'use_create_lots' is enabled.
        """
        if self.use_create_lots and self.picking_type_id.code == "incoming":
            lot = None  # This will hold the new lot for all move lines in the picking.

            # Loop through the move lines to create a new lot for the product
            for move_line in self.move_line_ids_without_package:
                if move_line.product_id.tracking == "lot" and move_line.product_id.purchase_ok:
                    # Create a new lot for the first valid move line
                    if not lot:
                        # Generate a new lot name based on product and current date
                        lot_name = f"LOT-{move_line.product_id.default_code}-{self.date_done.strftime('%d%m%y') if self.date_done else date.today().strftime('%d%m%y')}"

                        # Create the new lot
                        lot = self.env["stock.lot"].create({
                            "name": lot_name,
                            "product_id": move_line.product_id.id,
                            "company_id": self.company_id.id,
                            "product_qty": sum([line.qty_done for line in self.move_line_ids_without_package if
                                                line.product_id == move_line.product_id]),
                        })

                    # Assign the created lot to the move line
                    move_line.lot_id = lot.id

        return True
