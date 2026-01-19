from odoo import models, fields, api
from collections import defaultdict
from datetime import date
from odoo.exceptions import UserError
import logging
import calendar
import base64
import io
import xlsxwriter
import json

_logger = logging.getLogger(__name__)


class AccountMoveComparisonWizard(models.TransientModel):
    _name = "account.move.comparison.wizard"
    _description = "Compare Monthly Totals Across Years"

    start_date = fields.Date(
        string="Date Debut", default=lambda self: date(date.today().year, 1, 1)
    )
    end_date = fields.Date(
        string="Date Fin", default=lambda self: date(date.today().year, 12, 31)
    )
    years_to_compare = fields.Integer(string="Number of Years", default=3)
    results = fields.Text(string="Results", readonly=True)
    customer_ids = fields.Many2many("res.partner", string="Clients")

    invoice_user_id = fields.Many2one(
        comodel_name="res.users",
        string="Sales Team",
        help="Select the Sales Team to associate it with Sale Order.",
    )

    product_ids = fields.Many2many(
        "product.product",
        string="Products"
    )

    company_id = fields.Many2one(
        "res.company",
        string="Société",
        required=True,
        readonly=True,
        default=lambda self: self.env.company,
    )

    direction = fields.Selection(
        selection=[("up", "Up"), ("down", "Down"), ("same", "Same")],
        string="Direction",
        default="same",
    )

    report_template = fields.Selection(
        [
            ("account_move_period_comparison", "Comparasiosn Chiffre d’affaire par Période",),
            ("order_cycle_time", "Comparasiosn Chiffre d’affaire par Article"),
            ("account_move_region_comparison", "Comparasiosn Chiffre d’affaire par Région",),
            ("cost_reduction", "Réduction des coûts"),
            ("stock_turnover", "Taux de rotation des stocks"),
            ("account_ca_global", "Chiffre d’affaires"),
        ],
        string="Template de rapport",
        default="account_move_period_comparison",  # choisissez un des codes ci-dessus
        required=True,
    )

    excel_file = fields.Binary("Excel File", readonly=True)
    excel_filename = fields.Char("Excel Filename")
    report_data_json = fields.Text("Report Data JSON")

    def action_compare_report(self):
        """Trigger the report generation."""
        _logger.info("==> action_compare_report triggered")
        data = self.get_report_data()
        if data:
            return self.env.ref(
                "sale_enhancement.customer_comparison_simulation"
            ).report_action(self, data={"data": data})
        else:
            raise UserError("No data available for the report.")

    def get_report_data(self) -> dict:
        """Fetch & prepare comparison data. Periods respect the selected date range
        and are shifted back by years_to_compare-1 years (same relative months).
        """
        _logger.info("Preparing Customer Invoice Totals Comparison report...")
        # Basic validation
        if not self.start_date or not self.end_date:
            _logger.warning("start_date or end_date missing - aborting report.")
            return {}

        # Helper: safely shift a date back N years (handles Feb 29 -> last day of Feb).
        def shift_years(d: date, years_back: int) -> date:
            target_year = d.year - years_back
            try:
                return d.replace(year=target_year)
            except ValueError:
                # e.g. Feb 29 -> adjust to last day of Feb in target year
                last_day = calendar.monthrange(target_year, d.month)[1]
                return d.replace(year=target_year, day=min(d.day, last_day))

        # Helper: return list of 'YYYY-MM' between start and end inclusive
        def months_range(start_dt: date, end_dt: date):
            months = []
            cur_year, cur_month = start_dt.year, start_dt.month
            end_year, end_month = end_dt.year, end_dt.month
            while (cur_year, cur_month) <= (end_year, end_month):
                months.append(f"{cur_year}-{cur_month:02d}")
                # increment month
                if cur_month == 12:
                    cur_month = 1
                    cur_year += 1
                else:
                    cur_month += 1
            return months

        # Build periods (list of dicts) and compute overall search range (earliest_start, latest_end)
        periods = []
        start_dates = []
        end_dates = []
        report_data = []
        for i in range(self.years_to_compare):
            s_i = shift_years(self.start_date, i)
            e_i = shift_years(self.end_date, i)
            start_dates.append(s_i)
            end_dates.append(e_i)
            months = months_range(s_i, e_i)
            # friendly label: "01/01/2025 - 31/03/2025"
            label = f"{s_i.strftime('%d/%m/%Y')} - {e_i.strftime('%d/%m/%Y')}"
            periods.append(
                {
                    "index": i + 1,
                    "year": s_i.year,  # anchor year (the start-year)
                    "start_date": s_i,
                    "end_date": e_i,
                    "months": months,
                    "label": label,
                }
            )

        # Overall domain range - include all invoices across all periods
        earliest_start = min(start_dates)
        latest_end = max(end_dates)

        _logger.info(
            "Report periods built. earliest_start=%s latest_end=%s period_count=%s",
            earliest_start,
            latest_end,
            len(periods),
        )

        # Build search domain (cover all shifted periods)
        domain = [("move_type", "in", ("out_invoice", "out_refund"))]
        if self.customer_ids:
            domain.append(("partner_id", "in", self.customer_ids.ids))
        # Invoice date range must cover earliest_start..latest_end (string format)
        domain.append(("invoice_date", ">=", earliest_start.strftime("%Y-%m-%d")))
        domain.append(("invoice_date", "<=", latest_end.strftime("%Y-%m-%d")))
        domain.append(("company_id", "=", self.company_id.id))
        if self.invoice_user_id:
            domain.append(("invoice_user_id", "=", self.invoice_user_id.id))
        if self.product_ids:
            domain.append(('invoice_line_ids.product_id', 'in', self.product_ids.ids))

        _logger.debug("Searching invoices with domain: %s", domain)
        invoices = self.env["account.move"].search(domain, order="invoice_date")
        _logger.info("Found %d invoices in domain.", len(invoices))
        if not invoices:
            _logger.warning("No invoices found for expanded comparison range.")
            # still return periods so template can render headers
            return {
                "report_name": "Customer Invoice Totals Comparison",
                "years_to_compare": self.years_to_compare,
                "report_data": [],
                "start_date": self.start_date.strftime("%Y-%m-%d"),
                "end_date": self.end_date.strftime("%Y-%m-%d"),
                "customers": [c.name for c in (self.customer_ids or [])],
                "periods": periods,
                "grand_totals": {},
            }
        # Aggregate amounts per customer per month (YYYY-MM)
        customer_totals = defaultdict(lambda: defaultdict(float))
        if self.report_template == "account_move_period_comparison":
            for inv in invoices:
                inv_date = inv.invoice_date
                if not inv_date:
                    continue
                ym = f"{inv_date.year}-{inv_date.month:02d}"
                customer_totals[inv.partner_id.id][ym] += inv.amount_untaxed_signed

            # Bulk fetch partner names
            partner_ids = list(customer_totals.keys())
            partners = {p.id: p.name for p in self.env["res.partner"].browse(partner_ids)}

            # Prepare report rows and grand totals
            grand_totals = {}
            report_data = []
            # initialize grand_totals keys
            for period in periods:
                key = f"period_{period['index']}_{period['year']}"
                grand_totals[key] = 0.0

            for customer_id, totals in customer_totals.items():
                row = {"customer": partners.get(customer_id, "Unknown")}
                for period in periods:
                    key = f"period_{period['index']}_{period['year']}"
                    period_total = sum(totals.get(month, 0.0) for month in period["months"])
                    period_total = round(period_total, 2)
                    row[key] = period_total
                    grand_totals[key] = round(grand_totals.get(key, 0.0) + period_total, 2)
                report_data.append(row)

            # Optionally append a totals row (uncomment if you want it in report_data)
            totals_row = {"customer": "TOTAL"}
            for period in periods:
                key = f"period_{period['index']}_{period['year']}"
                totals_row[key] = grand_totals.get(key, 0.0)
            # report_data.append(totals_row)  # you can append if you want a totals row as a customer-like row

            _logger.info("Prepared report_data for %d customers", len(report_data))
            return {
                "report_name": self.report_template,
                "years_to_compare": self.years_to_compare,
                "report_data": report_data,
                "start_date": self.start_date.strftime("%Y-%m-%d"),
                "end_date": self.end_date.strftime("%Y-%m-%d"),
                "customers": [c.name for c in (self.customer_ids or [])],
                "periods": periods,  # use this in the QWeb template
                "grand_totals": grand_totals,  # totals per period
            }
            # *************************************
            #  TEMPLATE 2 — ORDER CYCLE TIME
            # *************************************
        elif self.report_template == "order_cycle_time":
            # Build domain for account.move.line
            domain = [
                ("move_id.move_type", "in", ("out_invoice", "out_refund")),
                ("date", ">=", earliest_start.strftime("%Y-%m-%d")),
                ("date", "<=", latest_end.strftime("%Y-%m-%d")),
                ("move_id.company_id", "=", self.company_id.id)
            ]
            if self.customer_ids:
                domain.append(("partner_id", "in", self.customer_ids.ids))
            if self.product_ids:
                domain.append(("product_id", "in", self.product_ids.ids))

            # Fetch all lines in the date range
            lines = self.env["account.move.line"].search(domain, order="date")
            if not lines:
                return {
                    "report_name": self.report_template,
                    "years_to_compare": self.years_to_compare,
                    "report_data": [],
                    "start_date": self.start_date.strftime("%Y-%m-%d"),
                    "end_date": self.end_date.strftime("%Y-%m-%d"),
                    "customers": [c.name for c in (self.customer_ids or [])],
                    "periods": periods,
                    "grand_totals": {},
                }

            # Aggregate per customer -> month -> product
            customer_data = defaultdict(
                lambda: defaultdict(lambda: defaultdict(lambda: {"balance": 0.0, "quantity": 0.0}))
            )

            for line in lines:
                if not line.date or not line.partner_id or not line.product_id:
                    continue
                ym = f"{line.date.year}-{line.date.month:02d}"
                balance = abs(line.price_subtotal) if line.price_subtotal < 0 else line.price_subtotal
                customer_data[line.partner_id.id][ym][line.product_id.name]["balance"] += balance
                customer_data[line.partner_id.id][ym][line.product_id.name]["quantity"] += line.quantity

            # Get customer names
            partner_ids = list(customer_data.keys())
            partners = {p.id: p.name for p in self.env["res.partner"].browse(partner_ids)}

            # Prepare report data
            report_data = []
            grand_totals = defaultdict(lambda: {"balance": 0.0, "quantity": 0.0})

            for customer_id, months in customer_data.items():
                row = {"customer": partners.get(customer_id, "Unknown")}

                # Collect all products for this customer
                all_products_set = set()
                for mdata in months.values():
                    all_products_set.update(mdata.keys())
                all_products = sorted(all_products_set)
                row['all_products'] = all_products

                # Prepare products_data per period
                for period in periods:
                    key = f"period_{period['index']}_{period['year']}"
                    row[key] = {"products_data": {}}

                    # Initialize products_data
                    for product in all_products:
                        row[key]["products_data"][product] = {"balance": 0.0, "quantity": 0.0}

                    # Sum per product for this period
                    for m in period["months"]:
                        mdata = months.get(m, {})
                        for product, pdata in mdata.items():
                            if product in row[key]["products_data"]:
                                row[key]["products_data"][product]["balance"] += pdata["balance"]
                                row[key]["products_data"][product]["quantity"] += pdata["quantity"]

                    # Sum period totals
                    period_balance = sum(p["balance"] for p in row[key]["products_data"].values())
                    period_qty = sum(p["quantity"] for p in row[key]["products_data"].values())
                    row[key]["balance"] = round(period_balance, 3)
                    row[key]["quantity"] = round(period_qty, 0)

                    # Add to grand totals
                    grand_totals[key]["balance"] += row[key]["balance"]
                    grand_totals[key]["quantity"] += row[key]["quantity"]

                report_data.append(row)

            return {
                "report_name": self.report_template,
                "years_to_compare": self.years_to_compare,
                "report_data": report_data,
                "start_date": self.start_date.strftime("%Y-%m-%d"),
                "end_date": self.end_date.strftime("%Y-%m-%d"),
                "customers": [c.name for c in (self.customer_ids or [])],
                "periods": periods,
                "grand_totals": grand_totals,
            }

        # *************************************
        #  TEMPLATE 3 — REGION COMPARISON
        # *************************************
        elif self.report_template == "account_move_region_comparison":
            return {
                "report_name": self.report_template,
                "periods": periods,
                "customers": [c.name for c in self.customer_ids],
                "start_date": self.start_date.strftime("%Y-%m-%d"),
                "end_date": self.end_date.strftime("%Y-%m-%d"),
            }

        # *************************************
        #  TEMPLATE 4 — COST REDUCTION
        # *************************************
        elif self.report_template == "cost_reduction":
            return {
                "report_name": self.report_template,
                "periods": periods,
                "customers": [c.name for c in self.customer_ids],
                "start_date": self.start_date.strftime("%Y-%m-%d"),
                "end_date": self.end_date.strftime("%Y-%m-%d"),
            }

        # *************************************
        #  TEMPLATE 5 — GLOBAL REVENUE
        # *************************************
        elif self.report_template == "account_ca_global":

            for inv in invoices:

                # Set sign based on refund
                sign = -1 if inv.move_type == "out_refund" else 1

                for line in inv.invoice_line_ids:

                    # Get category second-level name
                    display_name = line.product_id.categ_id.display_name or ""
                    parts = display_name.split('/')
                    second_part = parts[1].strip() if len(parts) > 1 else ""

                    # Exclude category "Timbre"
                    if second_part.lower() == "timbre":
                        continue
                    if not second_part:
                        continue

                    pkg = line.product_id.packaging_ids.filtered(lambda p: p.name and p.name.startswith('C'))
                    product_packaging_qty = pkg.qty if pkg else 0.0

                    report_data.append({
                        "invoice_number": inv.name,
                        "invoice_date": inv.invoice_date.strftime("%Y-%m-%d") if inv.invoice_date else "",
                        "customer": inv.partner_id.name,
                        "quantity": sign * line.quantity,
                        "product_id": sign * line.product_id.name,
                        "barcode": sign * line.product_id.barcode,
                        "extra_description": line.extra_description or '',
                        "PCB": product_packaging_qty,
                        "NBC": round(line.quantity / product_packaging_qty),
                        "ref": inv.ref,
                        "unit_price": round(sign * line.price_unit, 3),
                        "unit_price_after_discount": round(sign * line.price_unit * (1 - line.discount / 100), 3),
                        "discount": line.discount,
                        "total_before_discount": round(sign * line.price_unit * line.quantity, 3),
                        "total_after_discount": round(sign * line.price_subtotal, 3),
                        "product_category": second_part,
                    })
                self.report_data_json = json.dumps(report_data)

            return {
                "report_name": self.report_template,
                "report_data": report_data,
                "start_date": self.start_date.strftime("%Y-%m-%d"),
                "end_date": self.end_date.strftime("%Y-%m-%d"),
                "customers": [c.name for c in getattr(self, "customer_ids", [])] if getattr(self, "customer_ids",
                                                                                            False) else [],
            }


        # *************************************
        # UNKNOWN TEMPLATE
        # *************************************
        else:
            _logger.warning("Unknown report_template: %s", self.report_template)
            return {}

    def action_export_excel(self):
        self.ensure_one()

        # 1) Ensure report_data exists
        if not self.report_data_json:
            raise UserError("Aucune donnée du rapport à exporter.")

        # 2) Load report data from JSON
        report_data = json.loads(self.report_data_json)
        if not report_data:
            raise UserError("Aucune donnée du rapport à exporter.")

        # 3) Create Excel filename
        today_year = fields.Date.today().strftime("%Y")
        filename = f"Global_Revenue_Report_{today_year}.xlsx"

        # 4) Create workbook
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})
        worksheet = workbook.add_worksheet("Revenus")

        # 5) Formatting
        bold = workbook.add_format({"bold": True, "bg_color": "#D9E1F2"})
        date_format = workbook.add_format({"num_format": "yyyy-mm-dd"})
        number_format = workbook.add_format({"num_format": "#,##0.000"})

        # 6) Excel headers (matching the HTML order)
        headers = [
            "Date",
            "Inv #",
            "Ref #",
            "Code A barre",
            "Produit",
            "PCB",
            "NB C",
            "Qty",
            "Unit TND",
            "Unit TND (Disc)",
            "Disc %",
            "Total TND",
            "Total TND (Disc)",
            "Prod Cat",
            "Comment",
        ]

        for col, header in enumerate(headers):
            worksheet.write(0, col, header, bold)
            worksheet.set_column(col, col, 15)

        # 7) Fill rows
        for row, r in enumerate(report_data, start=1):
            # Date column
            inv_date = r.get("invoice_date")
            if inv_date:
                try:
                    inv_date_dt = fields.Date.from_string(inv_date)
                    worksheet.write_datetime(row, 0, inv_date_dt, date_format)
                except Exception:
                    worksheet.write(row, 0, inv_date)
            else:
                worksheet.write(row, 0, "")

            worksheet.write(row, 1, r.get("invoice_number", ""))
            worksheet.write(row, 2, r.get("ref", ""))
            worksheet.write(row, 3, r.get("barcode", ""))
            worksheet.write(row, 4, r.get("product_id", ""))
            worksheet.write_number(row, 5, r.get("PCB", 0))
            worksheet.write_number(row, 6, r.get("NBC", 0))
            worksheet.write_number(row, 7, r.get("quantity", 0), number_format)
            worksheet.write_number(row, 8, r.get("unit_price", 0), number_format)
            worksheet.write_number(row, 9, r.get("unit_price_after_discount", 0), number_format)
            worksheet.write_number(row, 10, r.get("discount", 0))
            worksheet.write_number(row, 11, r.get("total_before_discount", 0), number_format)
            worksheet.write_number(row, 12, r.get("total_after_discount", 0), number_format)
            worksheet.write(row, 13, r.get("product_category", ""))
            worksheet.write(row, 14, r.get("extra_description", ""))

        # 8) Close workbook
        workbook.close()
        output.seek(0)
        data = output.read()

        # 9) Save file to record
        self.excel_file = base64.b64encode(data)
        self.excel_filename = filename

        # 10) Trigger file download
        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{self._name}/{self.id}/excel_file/{self.excel_filename}?download=true",
            "target": "self",
        }


class PurchaseReport(models.AbstractModel):
    _name = "report.move_comparisonreport_template"
    _description = "Purchase Report"

    def _get_report_values(self, docids, data=None):
        data = data or {}
        report_data = data.get("data", {})
        return {
            "doc_ids": docids or [],
            "doc_model": "account.move.comparison.wizard",
            "data": report_data,
            "docs": self.env["account.move.comparison.wizard"].browse(docids),
        }
