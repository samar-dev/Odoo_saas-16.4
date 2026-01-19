from odoo import api, fields, models
from datetime import datetime
from odoo.exceptions import UserError
import base64
import io
from os.path import join as opj


class CNSSDeclaration(models.Model):
    _name = "cnss.declaration"
    _description = "CNSS Declaration"

    name = fields.Char(
        string="Reference", required=True, copy=False, readonly=True, default="New"
    )
    date_from = fields.Date(string="Start Date", required=True)
    date_to = fields.Date(string="End Date", required=True)
    line_ids = fields.One2many(
        "cnss.declaration.line", "declaration_id", string="Declaration Lines"
    )
    total_employee_cnss = fields.Float(
        string="Total Employee CNSS", compute="_compute_totals", store=True
    )
    total_employer_cnss = fields.Float(
        string="Total Employer CNSS", compute="_compute_totals", store=True
    )
    total_amount = fields.Float(
        string="Total Amount", compute="_compute_totals", store=True
    )
    state = fields.Selection([("draft", "Draft"), ("done", "Done")], default="draft")

    data = fields.Binary(string="Fichier CNSS", readonly=True)
    file_name = fields.Char(string="Nom du fichier", readonly=True)
    active_file = fields.Boolean(string="Fichier généré", default=False)
    company_id = fields.Many2one(
        "res.company",
        string="Société",
        default=lambda self: self.env.company,
        required=True,
    )
    num_trimester = fields.Selection(
        [("1", "1"), ("2", "2"), ("3", "3"), ("4", "4")],
        string="Numéro du trimestre",
        required=True,
    )

    @api.depends("line_ids.employee_cnss", "line_ids.employer_cnss")
    def _compute_totals(self):
        for rec in self:
            rec.total_employee_cnss = sum(line.employee_cnss for line in rec.line_ids)
            rec.total_employer_cnss = sum(line.employer_cnss for line in rec.line_ids)
            rec.total_amount = rec.total_employee_cnss + rec.total_employer_cnss

    def action_generate_lines(self):
        self.ensure_one()
        # Remove old lines
        self.line_ids.unlink()

        payslip_model = self.env["hr.payslip"]
        payslip_line_model = self.env["hr.payslip.line"]

        payslips = payslip_model.search(
            [
                ("date_from", ">=", self.date_from),
                ("date_to", "<=", self.date_to),
            ]
        )

        cnss_lines = payslip_line_model.search(
            [
                ("slip_id", "in", payslips.ids),
                ("name", "=", "CNSS"),
            ]
        )

        employees = cnss_lines.mapped("slip_id.employee_id")

        # Déterminer les mois de la période (3 max)
        months = []
        current_date = self.date_from
        while current_date <= self.date_to and len(months) < 3:
            months.append(current_date.month)
            year = current_date.year + (current_date.month // 12)
            month = current_date.month % 12 + 1
            current_date = datetime(year, month, 1).date()

        lines_vals = []
        for employee in employees:
            employee_lines = cnss_lines.filtered(
                lambda l: l.slip_id.employee_id == employee
            )
            employee_cnss_total = sum(employee_lines.mapped("total"))

            remunerations = []
            for month in months:
                payslip_for_month = payslip_model.search(
                    [
                        ("employee_id", "=", employee.id),
                        (
                            "date_from",
                            ">=",
                            datetime(self.date_from.year, month, 1).date(),
                        ),
                        (
                            "date_to",
                            "<=",
                            datetime(self.date_from.year, month, 28).date(),
                        ),
                        ("state", "=", "done"),
                    ],
                    limit=1,
                )
                if payslip_for_month:
                    contract = self.env["hr.contract"].search(
                        [
                            ("employee_id", "=", employee.id),
                            ("state", "=", "open"),
                        ],
                        limit=1,
                    )
                    remuneration = contract.wage if contract else 0.0
                else:
                    remuneration = 0.0
                remunerations.append(remuneration)

            lines_vals.append(
                (
                    0,
                    0,
                    {
                        "employee_id": employee.id,
                        "employee_cnss": employee_cnss_total,
                        "employer_cnss": 0.0,
                        "remuneration_1": (
                            remunerations[0] if len(remunerations) > 0 else 0.0
                        ),
                        "remuneration_2": (
                            remunerations[1] if len(remunerations) > 1 else 0.0
                        ),
                        "remuneration_3": (
                            remunerations[2] if len(remunerations) > 2 else 0.0
                        ),
                        "total": (
                            employee_cnss_total if employee_cnss_total > 0 else 0.0
                        ),
                    },
                )
            )

        self.line_ids = lines_vals

    def _get_file_lines(self):
        self.ensure_one()
        self.active_file = True

        chs = ""
        ch_cnss_company = str(self.company_id.company_registry or "").replace("-", "")
        while len(ch_cnss_company) < 10:
            ch_cnss_company = "0" + ch_cnss_company

        ch_exploi_company = str(self.company_id.company_registry or "")
        if len(ch_exploi_company) > 4:
            ch_exploi_company = ch_exploi_company[:4]
        while len(ch_exploi_company) < 4:
            ch_exploi_company = "0" + ch_exploi_company

        num_trimestre = self.num_trimester or "0"
        # On ne prend pas fiscalyear_id, on met une valeur fixe ou la date courante
        ch_year = fields.Date.today().strftime("%Y")

        ch_company = ch_cnss_company + ch_exploi_company + num_trimestre + ch_year

        for line in self.line_ids:
            ch_line = ch_company

            ch_num_order = str(line.id or 0)
            while len(ch_num_order) < 2:
                ch_num_order = "0" + ch_num_order

            ch_cnss_emp = str(line.employee_id.cnss_registration_number or "").replace(
                "-", ""
            )
            while len(ch_cnss_emp) < 10:
                ch_cnss_emp = "0" + ch_cnss_emp

            ch_nom_emp = str(line.employee_id.name or "").replace(" ", "")
            while len(ch_nom_emp) < 60:
                ch_nom_emp += " "

            ch_cin_emp = str(line.employee_id.identification_id or "")
            while len(ch_cin_emp) < 8:
                ch_cin_emp = "0" + ch_cin_emp

            total = round(line.total or 0.0, 3)
            d = (line.total or 0.0) - round(total)
            if d == 0:
                ch_wage_emp = str(int(total))
                while len(ch_wage_emp) < 10:
                    ch_wage_emp = "0" + ch_wage_emp
            else:
                wage_emp = str(total)
                pos = wage_emp.find(".")
                p = wage_emp[pos + 1 :] if pos != -1 else ""
                while len(p) < 3:
                    p += "0"
                ch_wage_emp = str(int(total)) + p
                while len(ch_wage_emp) < 10:
                    ch_wage_emp = "0" + ch_wage_emp

            ch_line += (
                ch_num_order
                + ch_cnss_emp
                + ch_nom_emp
                + ch_cin_emp
                + ch_wage_emp
                + "          "
            )

            chs += ch_line.upper() + "\n"
        return chs

    def generate_file(self):
        self.ensure_one()

        if not self.line_ids:
            raise UserError("Aucune ligne dans la déclaration pour générer le fichier.")

        # Nom du fichier sans fiscalyear_id, on utilise la date courante année
        today_year = fields.Date.today().strftime("%Y")
        cnss_code = (
            str(self.company_id.company_registry or "")
            .replace("-", "")[:10]
            .rjust(10, "0")
        )
        code_exploi = (self.company_id.company_registry or "")[:4].rjust(4, "0")
        filename = (
            f"DS{cnss_code}{code_exploi}{self.num_trimester or '0'}{today_year}.txt"
        )

        content = self._get_file_lines()
        if not content:
            raise UserError("Le contenu du fichier CNSS est vide.")

        self.data = base64.b64encode(content.encode("utf-8"))
        self.file_name = filename
        self.active_file = True
        return True

    def action_download_cnss_file(self):
        self.ensure_one()
        if not self.data:
            raise UserError("Veuillez générer le fichier avant de le télécharger.")
        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/cnss.declaration/{self.id}/data/{self.file_name}?download=true",
            "target": "self",
        }


class CNSSDeclarationLine(models.Model):
    _name = "cnss.declaration.line"
    _description = "CNSS Declaration Line"

    declaration_id = fields.Many2one(
        "cnss.declaration", string="Declaration", required=True, ondelete="cascade"
    )
    employee_id = fields.Many2one("hr.employee", string="Employee", required=True)
    employee_cnss = fields.Float(string="Employee CNSS Contribution")
    employer_cnss = fields.Float(string="Employer CNSS Contribution")
    remuneration_1 = fields.Float(string="Rémunération Mois 1")
    remuneration_2 = fields.Float(string="Rémunération Mois 2")
    remuneration_3 = fields.Float(string="Rémunération Mois 3")
    total = fields.Float(string="Total")
