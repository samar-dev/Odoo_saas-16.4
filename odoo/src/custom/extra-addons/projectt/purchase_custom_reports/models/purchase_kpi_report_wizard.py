import logging
from datetime import datetime, date
from odoo import models, fields
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PurchaseReportWizard(models.TransientModel):
    _name = "purchase.kpi.report.wizard"
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
            ("supplier_compliance", "Taux de conformité fournisseur"),
            ("order_cycle_time", "Cycle moyen de commande"),
            ("cost_reduction", "Réduction des coûts"),
            ("stock_turnover", "Taux de rotation des stocks"),
            ("urgent_purchases", "Taux d’achats en urgence"),
            ("spending_control", "Dépense sous contrôle achats"),
        ],
        string="Template de rapport",
        default="supplier_compliance",
        required=True,
    )

    start_date = fields.Date(
        string="Date Debut", default=lambda self: date(date.today().year, 1, 1)
    )
    end_date = fields.Date(
        string="Date Fin", default=lambda self: date(date.today().year, 12, 31)
    )

    category_id = fields.Many2many(
        "res.partner.category",
        string="Etiquettes Affichage",
    )

    detailed_type = fields.Selection([
        ('all', 'Tous'),  # ← All option
        ('consu', 'Consommable'),
        ('service', 'Service'),
        ('product', 'Produit stockable'),
        ('event', "Ticket d'événement"),
    ], string="Type", default='all')

    def action_print_kpi_report(self):
        _logger.info("==> action_print_report triggered")
        data = self.get_report_data()
        if data:
            # Wrap data in another dict for QWeb context
            return self.env.ref(
                "purchase_custom_reports.purchase_kpi_report_action"
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
        _logger.warning(orders)
        if not orders:
            _logger.warning("No purchase orders found for the given criteria.")

            return {}

        # Taux de conformité fournisseur (inspiré de summary_per_po)
        if self.report_template == "supplier_compliance":
            po_summary = []
            total_orders = 0
            conforming_orders = 0
            total_quality_checks = 0
            non_conforming_quality_checks = 0

            for order in orders:
                # Filter valid order lines
                order_lines = order.order_line.filtered(lambda l: l.product_id)
                total_ordered = sum(line.product_qty for line in order_lines)
                total_received = sum(line.qty_received for line in order_lines)

                # Quantity compliance
                qty_ok = total_received >= total_ordered

                # Initialize quality variables
                quality_ok = True
                quality_checks_state = None
                quality_checks_total = 0
                quality_checks_passed = 0
                quality_compliance_rate = None
                status_abbrev = ""

                # Process incoming pickings that are done
                for picking in order.picking_ids.filtered(
                        lambda p: p.picking_type_id.code == "incoming" and p.state == "done"
                ):
                    checks = picking.check_ids
                    if checks:
                        if any(check.quality_state == "none" for check in checks):
                            quality_checks_state = "draft"
                            quality_ok = None
                            quality_compliance_rate = None
                            break
                        quality_checks_total += len(checks)
                        quality_checks_passed += sum(
                            1 for check in checks if check.quality_state in ("pass", "validated")
                        )

                # Update total quality checks and non-conforming
                total_quality_checks += quality_checks_total
                non_conforming_quality_checks += (quality_checks_total - quality_checks_passed)

                # Compute compliance rate
                if quality_checks_total > 0 and quality_checks_passed > 0:
                    quality_compliance_rate = (quality_checks_passed / quality_checks_total) * 100
                    quality_ok = True
                elif quality_checks_total == 0:
                    quality_ok = None
                    quality_compliance_rate = None
                    quality_checks_state = None
                elif quality_checks_total > 0 and quality_checks_passed == 0:
                    quality_ok = False
                    quality_compliance_rate = 0
                    quality_checks_state = None

                if qty_ok:
                    if quality_ok is True:
                        status_abbrev = "Q++|OK"
                    elif quality_ok is False:
                        status_abbrev = "Q++|NOK"
                    elif quality_ok is None:
                        status_abbrev = "Q++|N/A"
                else:
                    if quality_ok is True:
                        status_abbrev = "Q--|OK"
                    elif quality_ok is False:
                        status_abbrev = "Q--|NOK"
                    elif quality_ok is None:
                        status_abbrev = "Q--|N/A"

                # Overall conformity
                is_conforming = qty_ok and (quality_ok is True)
                if is_conforming:
                    conforming_orders += 1
                total_orders += 1

                # Quantity compliance %
                compliance = (total_received / total_ordered * 100) if total_ordered else 0.0

                # Append order summary
                po_summary.append({
                    "order_name": order.name,
                    "order_date": order.date_order,
                    "partner_name": order.partner_id.name if order.partner_id else "AUCUN",
                    "qty_ordered": total_ordered,
                    "qty_received": total_received,
                    "compliance_rate": round(compliance, 2),
                    "is_conforming": is_conforming,
                    "quantity_ok": qty_ok,
                    "quality_ok": quality_ok,
                    "quality_compliance_rate": (
                        round(quality_compliance_rate, 2) if quality_compliance_rate is not None else None
                    ),
                    "quality_checks_state": quality_checks_state,
                    "status_abbrev": status_abbrev,
                })

            overall_compliance_rate = (
                (conforming_orders / total_orders * 100) if total_orders else 0.0
            )
            overall_quality_compliance_rate = (
                (total_quality_checks - non_conforming_quality_checks) / total_quality_checks * 100
                if total_quality_checks else 0.0
            )

            return {
                "report_name": self.report_name,
                "report_template": self.report_template,
                "po_summary": po_summary,
                "total_orders": total_orders,
                "total_quality_checks": total_quality_checks,
                "non_conforming_quality_checks": non_conforming_quality_checks,
                "conforming_orders": conforming_orders,
                "overall_compliance_rate": round(overall_compliance_rate, 2),
                "overall_quality_compliance_rate": round(overall_quality_compliance_rate, 2),
            }
        elif self.report_template == "order_cycle_time":
            po_summary = []
            durations = []

            for order in orders:
                # 1. Start date
                bat_dates = [line.bat_date for line in order.order_line if line.bat_date]
                date_start = bat_dates[0] if bat_dates else order.date_order

                # 2. Gather done pickings
                done_pickings = [
                    p for p in order.picking_ids
                    if p.state == "done" and p.picking_type_id.code == "incoming"
                ]

                scheduled_dates = [p.scheduled_date for p in done_pickings if p.scheduled_date]
                done_dates = [p.date_done for p in done_pickings if p.date_done]

                # Normalize types (date vs datetime)
                def to_datetime(val):
                    if val and not isinstance(val, datetime):
                        return datetime.combine(val, datetime.min.time())
                    return val

                date_start = to_datetime(date_start)
                latest_scheduled = to_datetime(max(scheduled_dates)) if scheduled_dates else None
                latest_done = to_datetime(max(done_dates)) if done_dates else None

                # 3. Compute deltas
                delta_done_vs_start = (
                    (latest_done - date_start).days if latest_done and date_start else None
                )
                delta_scheduled_vs_start = (
                    (latest_scheduled - date_start).days if latest_scheduled and date_start else None
                )
                delta_done_vs_scheduled = (
                    (latest_done - latest_scheduled).days if latest_done and latest_scheduled else None
                )

                if delta_done_vs_start is not None:
                    durations.append(delta_done_vs_start)

                color_status = None
                if delta_scheduled_vs_start is not None and delta_done_vs_start is not None:
                    if delta_done_vs_start > delta_scheduled_vs_start:
                        color_status = "red"  # Late
                    elif delta_done_vs_start == delta_scheduled_vs_start:
                        color_status = "green"  # On time
                    else:
                        color_status = "yellow"  # Early

                po_summary.append({
                    "order_name": order.name,
                    "partner_name": order.partner_id.name,
                    "date_start": date_start.strftime("%Y-%m-%d") if date_start else None,
                    "scheduled_date": latest_scheduled.strftime("%Y-%m-%d") if latest_scheduled else None,
                    "done_date": latest_done.strftime("%Y-%m-%d") if latest_done else None,
                    "delta_done_vs_start": delta_done_vs_start,
                    "delta_scheduled_vs_start": delta_scheduled_vs_start,
                    "delta_done_vs_scheduled": delta_done_vs_scheduled,
                    "color_status": color_status,
                })

            avg_duration = round(sum(durations) / len(durations), 2) if durations else 0

            return {
                "report_name": self.report_name,
                "report_template": self.report_template,
                "average_cycle_days": avg_duration,
                "num_orders": len(orders),
                "po_summary": po_summary,
            }



        elif self.report_template == "cost_reduction":
            product_data = {}
            for order in orders:
                partner = order.partner_id
                for line in order.order_line.filtered(lambda l: l.product_id):
                    reduction=0
                    product = line.product_id
                    # Find supplier info for this vendor
                    supplierinfo = product.seller_ids.filtered(lambda s: s.partner_id == partner)
                    prix_initial = supplierinfo[:1].price if supplierinfo else product.list_price
                    prix_negocie = line.price_unit or 0.0
                    # Skip invalid data
                    if prix_initial <= 0:
                        continue
                    if prix_initial > 1 :
                        reduction = ((prix_initial - prix_negocie) / prix_initial) * 100
                    # Group by product
                    if product.id not in product_data:
                        product_data[product.id] = {
                            "product_name": product.display_name or product.name,
                            "total_initial": 0.0,
                            "total_negocie": 0.0,
                            "total_reduction": 0.0,
                            "count": 0,
                        }
                    prod_entry = product_data[product.id]
                    prod_entry["total_initial"] += prix_initial
                    prod_entry["total_negocie"] += prix_negocie
                    prod_entry["total_reduction"] += reduction
                    prod_entry["count"] += 1
            # Prepare summary list
            po_summary = []
            total_reductions = []
            for data in product_data.values():
                avg_reduction = data["total_reduction"] / data["count"]
                avg_initial = data["total_initial"] / data["count"]
                avg_negocie = data["total_negocie"] / data["count"]
                po_summary.append({
                    "product_name": data["product_name"],
                    "avg_initial_price": round(avg_initial, 3) if avg_initial > 1 else 0,
                    "avg_negocie_price": round(avg_negocie, 3),
                    "avg_reduction_percent": round(avg_reduction, 3),
                    "num_orders": data["count"],
                })
                total_reductions.append(avg_reduction)
            # Global summary
            overall_avg_reduction = round(sum(total_reductions) / len(total_reductions), 2) if total_reductions else 0.0
            return {
                "report_name": self.report_name,
                "report_template": self.report_template,
                "average_cost_reduction_percent": overall_avg_reduction,
                "num_products": len(po_summary),
                "po_summary": po_summary,

            }

        elif self.report_template == "stock_turnover":
            turnover_list = []
            po_summary = []
            domain = [("type", "=", "product")]
            if self.category_id:
                domain.append(("categ_id", "in", self.category_id.ids))
            products = self.env["product.product"].search(domain)
            for product in products:
                # Mouvements de stock pendant la période
                stock_moves = self.env["stock.move"].search(
                    [
                        ("product_id", "=", product.id),
                        ("state", "=", "done"),
                        ("date", ">=", self.start_date),
                        ("date", "<=", self.end_date),
                        ("location_id.usage", "=", "internal"),
                        ("location_dest_id.usage", "!=", "internal"),
                    ]
                )
                if stock_moves:
                    total_qty_moved = sum(abs(move.product_qty) for move in stock_moves)
                    stock_start = product.with_context(
                        to_date=self.start_date
                    ).qty_available
                    stock_end = product.with_context(
                        to_date=self.end_date
                    ).qty_available
                    average_stock = (stock_start + stock_end) / 2
                    rotation = (
                        total_qty_moved / average_stock if average_stock > 0 else 0
                    )
                    if rotation >= 6:

                        movement_status = "Fast rotation"
                    else:
                        movement_status = "Has rotation"
                else:
                    total_qty_moved = 0
                    average_stock = 0
                    rotation = 0
                    movement_status = "No movement"
                delay = product.seller_ids[0].delay if product.seller_ids else 14
                delta_days = (self.end_date - self.start_date).days or 1
                daily_consumption = total_qty_moved / delta_days
                consumption_during_delay = daily_consumption * delay
                orderpoint = self.env["stock.warehouse.orderpoint"].search(
                    [("product_id", "=", product.id)], limit=1
                )
                safety_stock = orderpoint.product_min_qty if orderpoint else 0
                current_stock = product.qty_available
                qty_to_reorder = max(
                    round(consumption_during_delay + safety_stock - current_stock, 2), 0
                )
                turnover_list.append(rotation)
                po_summary.append(
                    {
                        "product_name": product.name,
                        "total_qty_moved": round(total_qty_moved, 2),
                        "average_stock": round(average_stock, 2),
                        "rotation": round(rotation, 2),
                        "movement_status": movement_status,
                        "qty_to_reorder": qty_to_reorder,
                        "safety_stock": safety_stock,
                        "report_name": self.report_name,
                        "report_template": self.report_template,
                    }
                )

            avg_rotation = (
                round(sum(turnover_list) / len(turnover_list), 2)
                if turnover_list
                else 0
            )

            num_lines = len(po_summary)

            for item in po_summary:
                item["avg_rotation"] = avg_rotation

                item["num_lines"] = num_lines

            return {
                "report_name": self.report_name,
                "report_template": self.report_template,
                "average_stock_turnover": avg_rotation,
                "num_lines": num_lines,
                "po_summary": po_summary,
            }
        elif self.report_template == "urgent_purchases":
            urgent_lines = []
            po_summary = []
            urgency_threshold = 3  # nombre de jours max entre commande et livraison

            for order in orders:
                partner = order.partner_id
                for line in order.order_line:
                    if line.date_planned and order.date_order:
                        delta_days = (
                                line.date_planned.date() - order.date_order.date()
                        ).days
                        is_urgent = delta_days <= urgency_threshold
                        po_summary.append(
                            {
                                "order_name": order.name,
                                "partner_name": partner.name,
                                "product_name": line.product_id.name,
                                "date_order": order.date_order,
                                "date_planned": line.date_planned,
                                "delta_days": delta_days,
                                "is_urgent": is_urgent,
                                "report_name": self.report_name,
                                "report_template": self.report_template,
                            }
                        )
                        if is_urgent:
                            urgent_lines.append(line)

            total_lines = len(po_summary)
            urgent_count = len(urgent_lines)
            urgent_rate = (
                round((urgent_count / total_lines) * 100, 2) if total_lines else 0
            )

            # Ajouter à chaque ligne le taux global et nombre total pour affichage
            for item in po_summary:
                item["urgent_count"] = urgent_count
                item["total_lines"] = total_lines
                item["urgent_rate"] = urgent_rate

            return {
                "report_name": self.report_name,
                "report_template": self.report_template,
                "urgent_count": urgent_count,
                "total_lines": total_lines,
                "urgent_rate": urgent_rate,
                "po_summary": po_summary,
            }
        elif self.report_template == "spending_control":
            analytic_totals = {}
            summary = []

            # Recherche des lignes de facture fournisseur dans la période
            domain = [
                ("move_id.move_type", "=", "in_invoice"),
                ("date", ">=", self.start_date),
                ("date", "<=", self.end_date),
                ("analytic_distribution", "!=", False),
            ]
            lines = self.env["account.move.line"].search(domain)

            for line in lines:
                total_amount = abs(line.debit - line.credit)
                distribution = line.analytic_distribution or {}

                for analytic_id_str, percent in distribution.items():
                    analytic_id = int(analytic_id_str)
                    amount = total_amount * (percent / 100)

                    if analytic_id not in analytic_totals:
                        analytic_totals[analytic_id] = 0
                    analytic_totals[analytic_id] += amount

            # Récupérer les objets analytiques et créer la structure de rapport
            for analytic_id, real_spent in analytic_totals.items():
                analytic = self.env["account.analytic.account"].browse(analytic_id)
                budget = self._get_budget_for_analytic(
                    analytic, self.start_date, self.end_date
                )
                variance = budget - real_spent
                usage_rate = (real_spent / budget * 100) if budget else 0

                summary.append(
                    {
                        "analytic_name": analytic.name,
                        "budget": round(budget, 2),
                        "real_spent": round(real_spent, 2),
                        "variance": round(variance, 2),
                        "usage_rate": round(usage_rate, 2),
                        "report_name": self.report_name,
                        "report_template": self.report_template,
                    }
                )

            return {
                "report_name": self.report_name,
                "report_template": self.report_template,
                "po_summary": summary,
            }

        else:
            _logger.warning("Unknown report_template: %s", self.report_template)
            return {}

    def _get_budget_for_analytic(self, analytic, date_from, date_to):
        # Si pas de module budget : tu peux définir manuellement ou par config
        budgets = {
            "AL-JAZIRA": 100000,
            "ALJAZIRA OLIVES": 50000,
            "Transport": 20000,
        }
        return budgets.get(analytic.name, 0)


class PurchaseReport(models.AbstractModel):
    _name = "report.purchase_custom_reports.purchase_kpi_report_template"
    _description = "Purchase Report"

    def _get_report_values(self, docids, data=None):
        data = data or {}
        report_data = data.get("data", {})
        return {
            "doc_ids": docids or [],
            "doc_model": "purchase.kpi.report.wizard",
            "data": report_data,
            "docs": self.env["purchase.kpi.report.wizard"].browse(docids),
        }
