import logging
from datetime import date

from odoo import models, fields
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PurchaseReportWizard(models.TransientModel):
    _name = "purchase.report.wizard"
    _description = "Purchase Report Wizard"

    vendor_ids = fields.Many2many("res.partner", string="Fournisseurs")
    state = fields.Selection(
        [
            ("draft", "RFQ"),
            ("sent", "RFQ Sent"),
            ("purchase", "Purchase Order"),
            ("done", "Locked"),
            ("cancel", "Cancelled"),
        ],
        string="Status",
    )
    report_name = fields.Char(
        string="Nom du rapport",
    )
    report_template = fields.Selection(
        [
            ("summary_per_po", "ETAT PREVISIONNEL DES PAIEMENTS FOURNISSEURS"),
            ("line_items", "PLANNING DE REÇU DES ACHATS"),
            ("grouped_per_product", "ETAT DE SUIVI DES ECHEANCES DE LIVRAISON"),
        ],
        string="Template de rapport ",
        default="summary_per_po",
    )

    start_date = fields.Date(
        string="Date Debut", default=lambda self: date(date.today().year, 1, 1)
    )
    end_date = fields.Date(
        string="Date Fin", default=lambda self: date(date.today().year, 12, 31)
    )

    category_id = fields.Many2many(
        "res.partner.category",
        string="Categorie",
    )

    detailed_type = fields.Selection([
        ('all', 'Tous'),  # ← All option
        ('consu', 'Consommable'),
        ('service', 'Service'),
        ('product', 'Produit stockable'),
        ('event', "Ticket d'événement"),
    ], string="Type", default='all')

    def action_print_report(self):
        _logger.info("==> action_print_report triggered")
        data = self.get_report_data()
        if data:
            # Wrap data in another dict for QWeb context
            return self.env.ref(
                "purchase_custom_reports.purchase_report_action"
            ).report_action(self, data={"data": data})
        else:
            raise UserError("No data available for the report.")

    def get_report_data(self):
        _logger.info("Fetching report data...")

        domain = []
        if self.vendor_ids:
            domain.append(("partner_id", "in", self.vendor_ids.ids))
        if self.state:
            domain.append(("state", "=", self.state))
        if self.start_date:
            domain.append(("date_order", ">=", self.start_date))
        if self.end_date:
            domain.append(("date_order", "<=", self.end_date))
        if self.category_id:
            # Filter purchase orders where partner's categories include one of selected categories
            domain.append(("partner_id.category_id", "in", self.category_id.ids))
        if self.detailed_type and self.detailed_type != 'all':
            domain.append(("product_id.detailed_type", "=", self.detailed_type))

        orders = self.env["purchase.order"].search(domain, order="date_order")
        if not orders:
            _logger.warning("No purchase orders found for the given criteria.")
            return {}
        else:
            orders = orders.filtered(
                lambda po: any(
                    picking.state not in ("done", "cancel")
                    and picking.picking_type_id.code == "incoming"
                    for picking in po.picking_ids
                )
            )

        # 1) Summary per Purchase Order
        if self.report_template == "summary_per_po":
            po_summary = []

            for order in orders:
                total_ordered = sum(line.product_qty for line in order.order_line)
                total_received = sum(line.qty_received for line in order.order_line)
                total_invoiced = sum(
                    inv_line.price_subtotal
                    for inv in order.invoice_ids
                    for inv_line in inv.invoice_line_ids
                    if inv_line.purchase_line_id.order_id == order
                )
                total_amount = order.amount_total
                price_remaining = total_amount - total_invoiced

                # Exclure commandes livrées et payées
                if total_received >= total_ordered and price_remaining <= 0:
                    continue

                # Delivery status
                if order.state in ("draft", "sent"):
                    delivery_status = "Demande de prix"
                elif total_received >= total_ordered and total_ordered > 0:
                    delivery_status = "Delivered"
                elif total_received > 0:
                    delivery_status = "Partial"
                else:
                    delivery_status = "Not Delivered"

                # Payment status
                if (
                    all(
                        inv.payment_state == "paid"
                        for inv in order.invoice_ids
                        if inv.move_type in ("in_invoice", "in_refund")
                    )
                    and order.invoice_ids
                ):
                    payment_status = "Paid"
                elif any(
                    inv.payment_state in ("partial", "not_paid")
                    for inv in order.invoice_ids
                    if inv.move_type in ("in_invoice", "in_refund")
                ):
                    payment_status = "Partially Paid"
                else:
                    payment_status = "Not Paid"

                # Planned date (la plus tardive parmi les lignes)
                planned_dates = [
                    line.date_planned for line in order.order_line if line.date_planned
                ]
                date_planned = (
                    max(planned_dates).strftime("%Y-%m-%d") if planned_dates else "N/A"
                )

                po_summary.append(
                    {
                        "order_name": order.name,
                        "partner_name": order.partner_id.name,
                        "qty_received": total_received,
                        "qty_ordered": total_ordered,
                        "price_invoiced": round(total_invoiced, 3),
                        "price_remaining": round(price_remaining, 3),
                        "payment_method": order.payment_term_id.name or "N/A",
                        "incoterm": order.incoterm_id.name or "N/A",
                        "date_order": (
                            order.date_order.strftime("%Y-%m-%d")
                            if order.date_order
                            else "N/A"
                        ),
                        "date_planned": date_planned,
                        "currency": order.currency_id.name or "N/A",
                        "delivery_status": delivery_status,
                        "payment_status": payment_status,
                    }
                )

            return {
                "report_name": self.report_name,
                "report_template": self.report_template,
                "po_summary": po_summary,
            }

        # 2) Detailed Purchase Order Lines (flat list)
        elif self.report_template == "line_items":
            lines_data = []

            for line in orders.mapped("order_line"):
                order_state = line.order_id.state
                qty_ordered = line.product_qty
                qty_received = line.qty_received
                qty_remaining = qty_ordered - qty_received

                # Gestion du statut
                if order_state in ("draft", "sent"):
                    status = "Demande de prix"
                elif qty_received >= qty_ordered:
                    continue  # On ignore les lignes complètement livrées
                elif qty_received > 0:
                    status = "Partial"
                else:
                    status = "Not Delivered"

                lines_data.append(
                    {
                        "order_name": line.order_id.name,
                        "partner_name": line.order_id.partner_id.name,
                        "product_name": line.product_id.display_name,
                        "qty_ordered": qty_ordered,
                        "qty_received": qty_received,
                        "qty_remaining": qty_remaining,
                        "date_order": (
                            line.order_id.date_order.strftime("%Y-%m-%d")
                            if line.order_id.date_order
                            else "N/A"
                        ),
                        "date_planned": (
                            line.date_planned.strftime("%Y-%m-%d")
                            if line.date_planned
                            else "N/A"
                        ),
                        "bat_date": (
                            line.bat_date.strftime("%Y-%m-%d")
                            if line.bat_date
                            else "N/A"
                        ),
                        "status": status,
                    }
                )

            return {
                "report_name": self.report_name,
                "report_template": self.report_template,
                "lines_data": lines_data,
            }

        # 3) Grouped Report per Product
        elif self.report_template == "grouped_per_product":
            grouped = {}

            for line in orders.mapped("order_line"):
                order_state = line.order_id.state
                product = line.product_id.display_name

                # Ignorer les lignes livrées (sauf brouillon)
                if (
                    order_state not in ("draft", "sent")
                    and line.qty_received >= line.product_qty
                ):
                    continue

                if product not in grouped:
                    grouped[product] = []

                qty_ordered = line.product_qty
                qty_received = line.qty_received
                qty_remaining = qty_ordered - qty_received

                # Détermination du statut
                if order_state in ("draft", "sent"):
                    status = "Demande de prix"
                elif qty_received > 0:
                    status = "Partial"
                else:
                    status = "Not Received"

                grouped[product].append(
                    {
                        "order_name": line.order_id.name,
                        "partner_name": line.order_id.partner_id.name,
                        "qty_ordered": qty_ordered,
                        "qty_received": qty_received,
                        "qty_remaining": qty_remaining,
                        "date_order": (
                            line.order_id.date_order.strftime("%Y-%m-%d")
                            if line.order_id.date_order
                            else "N/A"
                        ),
                        "date_planned": (
                            line.date_planned.strftime("%Y-%m-%d")
                            if line.date_planned
                            else "N/A"
                        ),
                        "bat_date": (
                            line.bat_date.strftime("%Y-%m-%d")
                            if line.bat_date
                            else "N/A"
                        ),
                        "status": status,
                    }
                )

            return {
                "report_name": self.report_name,
                "report_template": self.report_template,
                "grouped_data": grouped,
            }

        else:
            _logger.warning("Unknown report_template: %s", self.report_template)
            return {}


class PurchaseReport(models.AbstractModel):
    _name = "report.purchase_custom_reports.purchase_report_template"
    _description = "Purchase Report"

    def _get_report_values(self, docids, data=None):
        data = data or {}
        report_data = data.get("data", {})
        return {
            "doc_ids": docids or [],
            "doc_model": "purchase.report.wizard",
            "data": report_data,
            "docs": self.env["purchase.report.wizard"].browse(docids),
        }
