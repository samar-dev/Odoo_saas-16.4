from odoo import models, api
from odoo.exceptions import ValidationError
import base64
import re


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        """Override to validate quantities, post invoice, and attach PDF automatically."""
        # Step 1: Validate quantities
        for move in self:
            if move.move_type != "out_invoice":
                continue

            sale_orders = move.invoice_line_ids.mapped("sale_line_ids.order_id")
            for sale_order in sale_orders:
                if sale_order.partner_id.x_invoice_policy != "delivery":
                    continue

                delivered_qty_per_line = {line.id: line.qty_delivered for line in sale_order.order_line}

                for inv_line in move.invoice_line_ids:
                    for sale_line in inv_line.sale_line_ids:
                        delivered_qty = delivered_qty_per_line.get(sale_line.id, 0.0)
                        if delivered_qty == 0:
                            continue
                        if inv_line.quantity > delivered_qty:
                            raise ValidationError(
                                f"Le produit '{inv_line.product_id.display_name}' est facturé ({inv_line.quantity}) "
                                f"plus que la quantité livrée ({delivered_qty}).\n"
                                "Impossible de valider la facture."
                            )

        # Step 2: Call the original post
        res = super().action_post()

        # Step 3: Attach PDF for each invoice
        for invoice in self.filtered(lambda m: m.move_type == "out_invoice"):
            # Generate PDF using the standard invoice report
            pdf_content = self.env['ir.actions.report']._render_qweb_pdf("account.account_invoices", invoice.id)[0]
            b64_pdf = base64.b64encode(pdf_content)
            pdf_name = re.sub(r'\W+', '', invoice.name) + '.pdf'

            self.env['ir.attachment'].create({
                'name': pdf_name,
                'type': 'binary',
                'datas': b64_pdf,
                'store_fname': pdf_name,
                'res_model': 'account.move',
                'res_id': invoice.id,
                'mimetype': 'application/pdf',
            })

        return res
