# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval
import base64
import io
import xlsxwriter


class ImexInventoryReportWizard(models.TransientModel):
    _name = "imex.inventory.report.wizard"
    _description = "Imex Inventory Report Wizard"

    date_from = fields.Date(string="Start Date")
    date_to = fields.Date(string="End Date")
    location_id = fields.Many2one(comodel_name="stock.location", string="Location")
    product_ids = fields.Many2many(comodel_name="product.product", string="Products")
    len_product = fields.Integer()
    product_category_ids = fields.Many2many(
        comodel_name="product.category", string="Product Categories"
    )
    is_groupby_location = fields.Boolean(
        string="Group Locations",
        default=True,
        help="If checked qty will groupby location mean count internal transfer qty else will not count internal transfer qty",
    )

    generate_xls_file = fields.Binary("Excel File", readonly=True)
    file_name = fields.Char("File Name", default="Inventory_Report.xlsx")

    @api.onchange("product_ids")
    def _onchange_product_ids(self):
        for record in self:
            record.len_product = len(record.product_ids)

    def _prepare_imex_inventory_report(self):
        return {
            "date_from": self.date_from or "1900-01-01",
            "date_to": self.date_to or fields.Date.context_today(self),
            "product_ids": [(6, 0, self.product_ids.ids)] or None,
            "location_id": self.location_id.id or None,
            "product_category_ids": [(6, 0, self.product_category_ids.ids)] or None,
            "is_groupby_location": self.is_groupby_location,
        }

    def button_view(self):
        vals = {}
        report = self.create(self._prepare_imex_inventory_report())

        self.env["imex.inventory.report"].init_results(report)
        action = self.env.ref(
            "imex_inventory_report.action_imex_inventory_report_tree_view"
        )
        vals = action.sudo().read()[0]
        context = vals.get("context", {})
        if context:
            context = safe_eval(context)
        context["filters"] = self._prepare_imex_inventory_report()
        vals["context"] = context
        return vals

    def button_view_details(self):
        vals = {}
        report = self.create(self._prepare_imex_inventory_report())
        init = self.env["imex.inventory.details.report"].init_results(report)
        details = self.env["imex.inventory.details.report"].search([])
        action = self.env.ref(
            "imex_inventory_report.action_imex_inventory_details_report"
        )
        vals = action.sudo().read()[0]
        context = vals.get("context", {})
        if context:
            context = safe_eval(context)
        context["active_ids"] = details.ids
        data = {
            "product_default_code": self.product_ids.default_code,
            "product_name": self.product_ids.name,
            "date_from": self.date_from or None,
            "date_to": self.date_to or fields.Date.context_today(self),
            "location": self.location_id.complete_name or None,
            "category": self.product_ids.categ_id.complete_name or None,
        }
        context["data"] = data
        vals["context"] = context
        return vals

    def export_to_excel(self):
        """Export the report data to an Excel file."""
        # 1️⃣ Préparation des données
        report_data = self.create(self._prepare_imex_inventory_report())

        # 2️⃣ Initialiser les résultats
        self.env["imex.inventory.details.report"].init_results(report_data)
        details = self.env["imex.inventory.details.report"].search([])

        # 4️⃣réation du fichier Excel en mémoire
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()

        # 🔹 En-têtes du fichier
        headers = [
            "Product Code",
            "Product Name",
            "Date",
            "refernce",
            "Location",
            "Product In",
            "Product Out",
            "Product Cost",
            "Net Amount",
        ]
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header)

        # 🔹 Écriture des lignes de données
        row = 1

        for detail in details:
            date_format = workbook.add_format(
                {"num_format": "yyyy-mm-dd"}
            )  # or 'mm/dd/yyyy' depending on your preference
            worksheet.write(row, 0, detail.product_id.default_code)
            worksheet.write(row, 1, detail.product_id.name)
            worksheet.write(row, 2, detail.date, date_format)
            worksheet.write(row, 3, detail.reference)
            worksheet.write(row, 4, detail.location_id.name)
            worksheet.write(row, 5, detail.product_in)
            worksheet.write(row, 6, detail.product_out)
            worksheet.write(row, 7, detail.unit_cost)
            worksheet.write(
                row, 8, (detail.product_in - detail.product_out) * detail.unit_cost
            )

            row += 1

        workbook.close()
        output.seek(0)
        file_data = output.read()

        # 5️⃣ Enregistrement du fichier Excel en base64
        self.write(
            {
                "generate_xls_file": base64.b64encode(file_data),
                "file_name": "Inventory_Report.xlsx",
            }
        )

        # 6️⃣ Retour du lien de téléchargement
        return {
            "type": "ir.actions.act_url",
            "target": "self",
            "url": f"/web/content?model=imex.inventory.report.wizard&download=true&field=generate_xls_file&filename={self.file_name}&id={self.id}",
        }
