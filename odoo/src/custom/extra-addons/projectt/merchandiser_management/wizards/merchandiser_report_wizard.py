from odoo import fields, models


class MerchandiserReportWizard(models.TransientModel):
    _name = "merchandiser.report.wizard"

    assortment_id = fields.Many2one("assortment", string="Assortment")
    date_assortment = fields.Date(string="Date Debut")
    date_end = fields.Date(string="Date Fin")
    partner_id = fields.Many2one("res.partner", string="Partner")
    store_ids = fields.Many2many("res.partner.store", string="Stores")

    def print_report(self):
        return self.env.ref(
            "merchandiser_management.action_report_merchandiser"
        ).report_action(self)

    def compute_report(self):
        self.ensure_one()  # if called on one record at a time

        # Search merchandise planning lines linked to this assortment
        # Start with empty domain
        domain = []

        # Add filters only if fields are set
        if self.assortment_id:
            domain.append(("assortment_id", "=", self.assortment_id.id))

        if self.date_assortment:
            domain.append(("merchandise_planning_id.create_date", ">=", self.date_assortment))
            domain.append(("merchandise_planning_id.create_date", "<=", self.date_end))

        if self.partner_id:
            domain.append(("merchandise_planning_id.partner_id", "=", self.partner_id.id))

        if self.store_ids:
            domain.append(("store_id", "in", self.store_ids.ids))

        # Perform the search
        merchandise_lines = self.env["merchandise.planning.line"].search(domain)

        lines = []

        if merchandise_lines:
            # Compute rupture stats
            rupture_rate = len(merchandise_lines.filtered(lambda ml: not ml.stock_out))
            rupture_percentage = (
                (rupture_rate / len(merchandise_lines)) * 100
                if merchandise_lines
                else 0
            )
            average_quantity = sum(ml.quantity for ml in merchandise_lines) / len(
                merchandise_lines
            )

            for ml in merchandise_lines:
                lines.append(
                    {
                        "barcode": ml.barcode,
                        "product_name": ml.product_id.name
                        or "",  # use product name from variant
                        "rupture_rate": f"{rupture_rate}/{len(merchandise_lines)}",
                        "rupture_percentage": round(rupture_percentage, 2),
                        "average_quantity": average_quantity,
                    }
                )
        else:
            # no lines → empty stats
            lines.append(
                {
                    "barcode": "",
                    "product_name": "",
                    "rupture_rate": "0/0",
                    "rupture_percentage": 0,
                    "average_quantity": 0,
                }
            )

        return lines

    def get_value(self, record, field):
        return record[field]
