from odoo import models, fields, api
from collections import defaultdict
from datetime import date
from io import BytesIO
import base64


class TreasurySummary(models.Model):
    _name = "treasury.summary"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Treasury Template Monthly Summary"

    name = fields.Char(string="Label", required=True, default="/")

    template_id = fields.Many2one(
        "treasury.template", string="Treasury Template", required=True
    )

    summary_line_ids = fields.One2many(
        "treasury.summary.line",
        "summary_id",
        string="Monthly Sector Summary",
        compute="_compute_summary_lines",
        store=True,
    )

    excel_file = fields.Binary(string="Excel Report", readonly=True)
    excel_filename = fields.Char(string="Excel Filename", readonly=True)

    def action_recompute_summary_lines(self):
        account_move_line = self.env["account.move.line"]

        for summary in self:
            result = defaultdict(
                lambda: defaultdict(float)
            )  # sector -> {month_str: amount}

            treasury_lines = summary.template_id.treasury_line_ids.filtered(
                lambda l: l.date and l.sector_id and l.account_treasury_ids
            )

            for line in treasury_lines:
                sector = line.sector_id
                start_month = line.date.month
                year = line.date.year

                for month_num in range(
                    start_month, 13
                ):  # From line.date.month to December
                    month_name = (
                        date(2000, month_num, 1).strftime("%b").lower()
                    )  # jan, feb, ...
                    month_start = date(year, month_num, 1)
                    if month_num == 12:
                        month_end = date(year + 1, 1, 1)
                    else:
                        month_end = date(year, month_num + 1, 1)

                    for treasury in line.account_treasury_ids:
                        domain = [("account_id", "=", treasury.account_id.id)]

                        if treasury.journal_ids:
                            domain.append(
                                ("journal_id", "in", treasury.journal_ids.ids)
                            )

                        domain += [
                            ("date", ">=", month_start),
                            ("date", "<", month_end),
                        ]

                        move_lines = account_move_line.search(domain)

                        amount = sum(
                            ml.debit if treasury.sens == "debit" else ml.credit
                            for ml in move_lines
                        )

                        result[sector][month_name] += amount

            # Clear previous summary lines
            summary.summary_line_ids = [(5, 0, 0)]

            new_lines = []
            months = [
                "jan",
                "feb",
                "mar",
                "apr",
                "may",
                "jun",
                "jul",
                "aug",
                "sep",
                "oct",
                "nov",
                "dec",
            ]

            for sector, month_amounts in result.items():
                vals = {"sector_id": sector.id}
                for month in months:
                    vals[month] = month_amounts.get(month, 0.0)
                new_lines.append((0, 0, vals))

            summary.summary_line_ids = new_lines

    def action_export_excel(self):
        import xlsxwriter

        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})
        worksheet = workbook.add_worksheet("Summary")

        # Write headers
        headers = [
            "Sector",
            "Janvier",
            "Février",
            "Mars",
            "Avril",
            "Mai",
            "Juin",
            "Juillet",
            "Août",
            "Septembre",
            "Octobre",
            "Novembre",
            "Décembre",
        ]

        header_format = workbook.add_format({"bold": True, "bg_color": "#D7E4BC"})
        money_format = workbook.add_format({"num_format": "#,##0.00"})

        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
            worksheet.set_column(col, col, 15)  # set column width

        row = 1
        for line in self.summary_line_ids:
            worksheet.write(row, 0, line.sector_id.name or "N/A")
            worksheet.write_number(row, 1, line.jan or 0.0, money_format)
            worksheet.write_number(row, 2, line.feb or 0.0, money_format)
            worksheet.write_number(row, 3, line.mar or 0.0, money_format)
            worksheet.write_number(row, 4, line.apr or 0.0, money_format)
            worksheet.write_number(row, 5, line.may or 0.0, money_format)
            worksheet.write_number(row, 6, line.jun or 0.0, money_format)
            worksheet.write_number(row, 7, line.jul or 0.0, money_format)
            worksheet.write_number(row, 8, line.aug or 0.0, money_format)
            worksheet.write_number(row, 9, line.sep or 0.0, money_format)
            worksheet.write_number(row, 10, line.oct or 0.0, money_format)
            worksheet.write_number(row, 11, line.nov or 0.0, money_format)
            worksheet.write_number(row, 12, line.dec or 0.0, money_format)
            row += 1

        workbook.close()
        output.seek(0)

        data = output.read()
        self.excel_file = base64.b64encode(data)
        self.excel_filename = f"Treasury_Summary_{self.id}.xlsx"

        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/treasury.summary/{self.id}/excel_file/{self.excel_filename}?download=true",
            "target": "self",
        }


class TreasurySummaryLine(models.Model):
    _name = "treasury.summary.line"
    _description = "Monthly Amounts by Sector"

    summary_id = fields.Many2one(
        "treasury.summary", string="Summary", ondelete="cascade", required=True
    )
    sector_id = fields.Many2one("purchase.sector", string="Sector", required=True)

    jan = fields.Float(string="Janvier")
    feb = fields.Float(string="Février")
    mar = fields.Float(string="Mars")
    apr = fields.Float(string="Avril")
    may = fields.Float(string="Mai")
    jun = fields.Float(string="Juin")
    jul = fields.Float(string="Juillet")
    aug = fields.Float(string="Août")
    sep = fields.Float(string="Septembre")
    oct = fields.Float(string="Octobre")
    nov = fields.Float(string="Novembre")
    dec = fields.Float(string="Décembre")
