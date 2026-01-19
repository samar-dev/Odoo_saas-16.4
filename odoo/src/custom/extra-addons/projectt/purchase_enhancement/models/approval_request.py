from odoo import models, api

class ApprovalRequestInherit(models.Model):
    _inherit = 'approval.request'

    def action_create_purchase_orders(self):
        """Override: call original method and then apply custom logic."""
        self.ensure_one()

        # --- Call the original method ---
        res = super(ApprovalRequestInherit, self).action_create_purchase_orders()

        # --- Custom logic: for example, force creating new POs ---
        # Create a dictionary to group product lines by vendor
        lines_by_vendor = {}
        for line in self.product_line_ids:
            seller = line._get_seller_id()
            vendor = seller.partner_id
            if vendor not in lines_by_vendor:
                lines_by_vendor[vendor] = []
            lines_by_vendor[vendor].append((line, seller))

        # Create one purchase order per vendor
        for vendor, line_seller_list in lines_by_vendor.items():
            # Use the first line to get default PO values
            first_line, first_seller = line_seller_list[0]
            po_vals = first_line._get_purchase_order_values(vendor)
            new_purchase_order = self.env['purchase.order'].create(po_vals)

            # Add all lines for this vendor
            for line, seller in line_seller_list:
                po_line_vals = self.env['purchase.order.line']._prepare_purchase_order_line(
                    line.product_id,
                    line.quantity,
                    line.product_uom_id,
                    line.company_id,
                    seller,
                    new_purchase_order,
                )
                new_po_line = self.env['purchase.order.line'].create(po_line_vals)
                line.purchase_order_line_id = new_po_line.id
                new_purchase_order.order_line = [(4, new_po_line.id)]

            # Ensure the approval request name is in the origin field
            new_purchase_order.write({'origin': self.name})

        return res

