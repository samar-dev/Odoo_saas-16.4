from odoo import models, fields, api
from datetime import date
import calendar
from collections import defaultdict
import time
import io
import base64
import xlsxwriter


class JournalPayPeriodique(models.Model):
    _name = "journal.pay.periodique"
    _description = "Journal Paie Périodique Résultats"

    employee_name = fields.Char()
    employee_matricule = fields.Char()
    salary_lines = fields.Json(string="Salary Lines")  # Store all dynamic totals here
    conge = fields.Float()
    base = fields.Float()
    indemnite_pr = fields.Float()
    indemnite_tr = fields.Float()
    indemnite_dif = fields.Float()
    cp_value = fields.Float()
    wage = fields.Float()
    cotisation_employee = fields.Float()
    salaire_brut_imposable = fields.Float()
    impo = fields.Float()
    impo_css = fields.Float()
    salaire_net = fields.Float()
    amount_avance = fields.Float()
    salaire_net_to_pay = fields.Float()
    salaire_round_pay = fields.Float()
    productivite_round_pay = fields.Float()
    end_yaer_round_pay = fields.Float()
    supplmentaires_round_pay = fields.Float()
    ferie_to_pay = fields.Float()
    rappel_to_pay = fields.Float()
    vca_round_pay = fields.Float()


class WizardJournalPayPeriodique(models.TransientModel):
    _name = "wizard.journal.pay.periodique"
    _description = "Wizard Journal Paie Périodique"

    year = fields.Selection(
        [(str(y), str(y)) for y in range(2020, 2031)],
        string="Année",
        required=True,
        default=lambda self: str(fields.Date.today().year),
    )
    month = fields.Selection(
        [(str(m), str(m)) for m in range(1, 13)],
        string="Début",
        required=True,
        default=lambda self: str(fields.Date.today().month),
    )
    month_end = fields.Selection(
        [(str(m), str(m)) for m in range(1, 13)],
        string="Fin",
        required=True,
        default=lambda self: str(fields.Date.today().month),
    )
    motif = fields.Char("Nom de la période")
    company_id = fields.Many2one(
        "res.company",
        string="Société",
        required=True,
        readonly=True,
        default=lambda self: self.env.company,
    )

    # Optional field to store Excel
    generate_xls_file = fields.Binary("Download Excel")
    file_name = fields.Char()

    def _prepare_report_data(self):
        """Prepare all report data without triggering QWeb"""
        self.env["journal.pay.periodique"].search([]).unlink()

        year = int(self.year)
        month_start = int(self.month)
        month_end = int(self.month_end)
        first_day = date(year, month_start, 1)
        last_day = date(year, month_end, calendar.monthrange(year, month_end)[1])

        domain = [
            ("date_from", ">=", first_day),
            ("date_to", "<=", last_day),
            ("company_id", "=", self.company_id.id),
        ]
        payslips = self.env["hr.payslip"].search(domain)
        totals = defaultdict(float)
        result = []

        # --- Prepare employee data ---
        for slip in payslips:
            emp = slip.employee_id
            payroll_lines = slip.line_ids.filtered(lambda l: l.salary_rule_id.appears_on_payroll_report)
            salary_lines = {}
            for line in payroll_lines:
                if line.salary_rule_id.rule_type != "money":
                    continue
                rule_name = line.salary_rule_id.name
                salary_lines[rule_name] = {
                    "amount": round(line.total, 3),
                    "sequence": line.salary_rule_id.sequence,
                }
                totals[rule_name] += line.total

            sorted_keys = list(salary_lines.keys())  # Temporary, will reorder later
            record = {
                "employee_name": emp.name,
                "employee_matricule": emp.pin or "",
                "salary_lines": salary_lines,
                "sorted_keys": sorted_keys,
            }

            self.env["journal.pay.periodique"].create({
                "employee_name": emp.name,
                "employee_matricule": emp.pin or "",
                "salary_lines": salary_lines
            })
            result.append(record)

        # ======================================================
        #   GLOBAL MASTER SEQUENCE
        # ======================================================
        grand_rule_sequences = {
            "Salaire de Base J": 10,
            "Jours de congés": 20,
            "Indemnité de présence": 30,
            "Indemnité différentielle": 40,
            "Indemnité de transport": 50,
            "PRIME RENDEMENT": 60,
            "Prime de productivité": 70,
            "Prime fin année": 80,
            "Valeur Conge Annuel": 90,
            "Valeur Solde Conge": 100,
            "Heures supplémentaires": 110,
            "JF + DIMANCHE": 120,
            "Rappel Salaire": 130,
            "Gratification de fin de service": 140,
            "Total Salaire Brut": 150,
            "CNSS": 160,
            "Salaire Imposable": 170,
            "IRPP": 180,
            "CSS 0.5%": 190,
            "SALAIRE NET AVANT DEDUCTIONS": 200,
            "Avances": 210,
            "Prêt": 220,
            "Arrondi": 230,
            "Net à payer": 240,
        }

        # All keys present in payslips
        all_emp_keys = {k for emp in result for k in emp["salary_lines"].keys()}

        # Keep only keys that exist in data
        final_global_order = [k for k in grand_rule_sequences.keys() if k in all_emp_keys]

        # ======================================================
        #   GROUPS OF 6 EMPLOYEES
        # ======================================================
        group_size = 6
        sorted_result = sorted(result, key=lambda r: r["employee_matricule"] or "")
        groups = []
        n = len(sorted_result)
        for i in range(0, n, group_size):
            group_employees = sorted_result[i:i + group_size]
            group_keys = {k for emp in group_employees for k in emp['salary_lines'].keys()}

            # --- APPLY GLOBAL SEQUENCE LOGIC ---
            precomputed_group_keys = [k for k in final_global_order if k in group_keys]

            groups.append({
                "employees": group_employees,
                "sorted_keys": precomputed_group_keys
            })

        return {
            "result": result,
            "groups": groups,
            "totals": dict(totals),
            "all_keys_total_sorted": final_global_order,
            "motif": self.motif
        }

    def print_report(self):
        """PDF/QWeb report"""
        data = self._prepare_report_data()
        return self.env.ref(
            "hr_payroll_enhancement.journal_pay_periodique_report_action"
        ).report_action(self, data=data)

    def export_to_excel(self):
        """Excel export"""
        data = self._prepare_report_data()
        result = data['result']
        all_keys_total_sorted = data['all_keys_total_sorted']
        totals = data['totals']

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("Payroll Report")

        headers = ["Employee Matricule", "Employee Name"] + all_keys_total_sorted + ["Total"]
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D9D9D9'})
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header, header_format)

        money_format = workbook.add_format({'num_format': '#,##0.00'})
        row = 1

        for emp in result:
            worksheet.write(row, 0, emp['employee_matricule'])
            worksheet.write(row, 1, emp['employee_name'])
            total_emp = 0
            for col_num, key in enumerate(all_keys_total_sorted, start=2):
                amount = emp['salary_lines'].get(key, {}).get('amount', 0.0)
                worksheet.write(row, col_num, amount, money_format)
                total_emp += amount
            worksheet.write(row, 2 + len(all_keys_total_sorted), total_emp, money_format)
            row += 1

        worksheet.write(row, 0, "Grand Total", header_format)
        worksheet.write(row, 1, "")
        for col_num, key in enumerate(all_keys_total_sorted, start=2):
            worksheet.write(row, col_num, totals.get(key, 0.0), money_format)
        total_all = sum(totals.get(key, 0.0) for key in all_keys_total_sorted)
        worksheet.write(row, 2 + len(all_keys_total_sorted), total_all, money_format)

        workbook.close()
        output.seek(0)
        file_data = output.read()

        self.write({
            "generate_xls_file": base64.b64encode(file_data),
            "file_name": "Payroll_Report.xlsx",
        })

        return {
            "type": "ir.actions.act_url",
            "target": "self",
            "url": f"/web/content?model={self._name}&download=true&field=generate_xls_file&filename={self.file_name}&id={self.id}",
        }



class ReportJournalPayPeriodique(models.AbstractModel):
    _name = "report.journal_pay_periodique.journal_pay_periodique_template"
    _description = "Report Journal Paie Périodique"

    @api.model
    def _get_report_values(self, docids, data=None):
        data = data or {}
        return {
            "doc_ids": docids,
            "doc_model": "wizard.journal.pay.periodique",
            "result": data.get("result", []),
            "totals": data.get("totals", {}),
            "motif": data.get("motif", ""),
            "time": time,
        }
