from odoo import models, fields, api
from odoo.tools import format_date
import io
import xlsxwriter
import base64
from odoo.exceptions import UserError


class PayrollPaymentOrder(models.Model):
    _name = "payroll.payment.order"
    _description = "Ordre de Virement Paie"

    name = fields.Char(string="Référence", required=True, default="Nouveau")
    date_from = fields.Date(string="Du", required=True)
    date_to = fields.Date(string="Au", required=True)
    date_order = fields.Date(
        string="Date", required=True, default=fields.Date.context_today
    )
    company_id = fields.Many2one(
        "res.company",
        string="Société",
        required=True,
        default=lambda self: self.env.company,
    )
    bank_id = fields.Many2one("res.partner.bank", string="Banque")
    currency_id = fields.Many2one(
        "res.currency",
        string="Devise",
        default=lambda self: self.env.company.currency_id,
    )
    payment_line_ids = fields.One2many(
        "payroll.payment.line", "order_id", string="Lignes de paiement"
    )
    total_amount = fields.Monetary(
        string="Montant Total",
        compute="_compute_total_amount",
        currency_field="currency_id",
    )

    excel_file = fields.Binary(string="Excel Export", readonly=True)
    excel_filename = fields.Char(string="Excel Filename")

    @api.depends("payment_line_ids.amount")
    def _compute_total_amount(self):
        for order in self:
            order.total_amount = sum(order.payment_line_ids.mapped("amount"))

    def action_generate_lines(self):
        self.ensure_one()
        # Supprimer les anciennes lignes
        self.payment_line_ids.unlink()

        payslip_model = self.env["hr.payslip"]
        payslip_line_model = self.env["hr.payslip.line"]

        # Cherche les fiches de paie dans la période
        payslips = payslip_model.search(
            [
                ("date_from", ">=", self.date_from),
                ("date_to", "<=", self.date_to),
                ("company_id", "=", self.company_id.id),
            ]
        )

        # Cherche les lignes de paie avec code NET (salaire net à payer)
        net_lines = payslip_line_model.search(
            [
                ("slip_id", "in", payslips.ids),
                ("code", "=", "NETAP"),
            ]
        )

        employees = net_lines.mapped("slip_id.employee_id")

        lines_vals = []
        for employee in employees:
            employee_lines = net_lines.filtered(
                lambda l: l.slip_id.employee_id == employee
            )
            net_total = sum(employee_lines.mapped("total"))

            bank_account = employee.bank_account_id
            bank = bank_account.bank_id if bank_account else False
            rib = employee.rib_number

            lines_vals.append(
                (
                    0,
                    0,
                    {
                        "employee_id": employee.id,
                        "bank_id": bank.id if bank else False,
                        "rib": rib,
                        "amount": net_total,
                        "currency_id": self.currency_id.id,
                    },
                )
            )

        self.payment_line_ids = lines_vals

    def action_export_excel(self):
        self.ensure_one()

        if not self.payment_line_ids:
            raise UserError("Aucune ligne de paiement pour générer le fichier Excel.")

        # Générer nom de fichier avec l'année courante et référence ordre paiement
        today_year = fields.Date.today().strftime("%Y")
        filename = f"OrdrePaiement_{self.name}_{today_year}.xlsx"

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})
        worksheet = workbook.add_worksheet("Paiements")

        bold = workbook.add_format({"bold": True})

        headers = [
            "RIB_DONNEUR",
            "NOM_DONNEUR",
            "RIB_BENEFICIAIRE",
            "NOM_BENEFICIAIRE",
            "MONTANT",
            "MOTIF_OPERATION",
            "DATE_EXECUTION",
        ]
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header, bold)

        row = 1
        date_format = workbook.add_format(
            {"num_format": "dd/mm/yyyy"}
        )  # format for date cells

        for line in self.payment_line_ids:
            worksheet.write(row, 0, self.bank_id.bank_id.name or "")
            worksheet.write(row, 1, self.company_id.name or "")
            worksheet.write(row, 2, line.rib or "")
            worksheet.write(row, 3, line.employee_id.name or "")
            worksheet.write(row, 4, (line.amount or 0.0) * 1000)
            worksheet.write(row, 5, self.name or "")
            # Write the date with date format
            worksheet.write_datetime(row, 6, self.date_order, date_format)
            row += 1
        workbook.close()
        output.seek(0)
        data = output.read()

        self.excel_file = base64.b64encode(data)
        self.excel_filename = filename

        # Optional: return action to download immediately
        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/payroll.payment.order/{self.id}/excel_file/{self.excel_filename}?download=true",
            "target": "self",
        }


class PayrollPaymentLine(models.Model):
    _name = "payroll.payment.line"
    _description = "Ligne de Virement Paie"

    order_id = fields.Many2one(
        "payroll.payment.order", string="Ordre", required=True, ondelete="cascade"
    )
    employee_id = fields.Many2one("hr.employee", string="Salarié", required=True)
    bank_id = fields.Many2one("res.bank", string="Banque")
    rib = fields.Char(string="RIB")
    amount = fields.Monetary(string="Montant", currency_field="currency_id")
    currency_id = fields.Many2one("res.currency", string="Devise")


class ReportPayrollPaymentOrder(models.AbstractModel):
    _name = "report.hr_payroll_enhancement.report_payroll_payment_order"
    _description = "Report Ordre de Virement Paie"

    def _get_report_values(self, docids, data=None):
        docs = self.env["payroll.payment.order"].browse(docids)

        def format_date_wrapper(date):
            return format_date(self.env, date)

        return {
            "doc_ids": docids,
            "doc_model": "payroll.payment.order",
            "docs": docs,
            "format_date": format_date_wrapper,
        }
