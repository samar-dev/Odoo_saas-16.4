from odoo import models, fields, api


class StockLocation(models.Model):
    _inherit = "stock.location"

    capacity_max = fields.Float("Capacité maximale", digits=(16, 3))
    capacity_occupied = fields.Float(
        "Capacité occupée", compute="_compute_capacity", store=True, digits=(16, 3)
    )
    occupancy_percent = fields.Float(
        "Taux occupation (%)", compute="_compute_capacity", store=True, digits=(16, 3)
    )
    capacity_status = fields.Selection(
        [("green", "Allowed"), ("orange", "Warning"), ("red", "Alert")],
        compute="_compute_capacity",
        store=True,
    )
    capacity_unit = fields.Selection(
        [("units", "Units"), ("kg", "Kilograms"), ("m3", "Cubic Meters")],
        string="Capacity Unit",
        default="units",
    )

    product_lot_info = fields.Text(
        string="Produits et lots", compute="_compute_product_lot_info"
    )
    product_lot_report = fields.Text(
        string="Produits et rapports", compute="_compute_product_lot_info"
    )
    product_txt = fields.Text(
        string="Produits", compute="_compute_product_lot_info"
    )

    row = fields.Integer(string="Row Position", help="Row position in tank grid")
    col = fields.Integer(string="Column Position", help="Column position in tank grid")

    @api.depends("capacity_max","quant_ids")
    def _compute_capacity(self):
        product_category_id = 937
        for location in self:
            # chercher les quants dont product appartient à la catégorie 937
            quants = self.env["stock.quant"].search(
                [
                    ("location_id", "=", location.id),
                    ("product_id.categ_id", "=", product_category_id),
                ]
            )
            occupied = sum(quants.mapped("quantity"))
            location.capacity_occupied = occupied
            if location.capacity_max > 0:
                percent = (occupied / location.capacity_max) * 100
            else:
                percent = 0.0
            location.occupancy_percent = round(percent, 2)
            if percent >= 100:
                status = "red"
            elif percent >= 80:
                status = "orange"
            else:
                status = "green"
            location.capacity_status = status

    def _compute_product_lot_info(self):
        product_category_id = 937
        for location in self:
            quants = self.env["stock.quant"].search(
                [
                    ("location_id", "=", location.id),
                    ("product_id.categ_id", "=", product_category_id),
                ]
            )
            lines = []
            lines_report = []
            for quant in quants:
                if quant.lot_id:
                    self.product_txt = quant.product_id.name
                    lot = quant.lot_id.name
                    numero_adm = quant.lot_id.numero_adm or ""
                    ac = quant.lot_id.ac or ""
                    k_two = quant.lot_id.k_two or 0.0
                    k_seven = quant.lot_id.k_seven or 0.0
                    pesticides = quant.lot_id.pesticides or 0.0
                    qty = round(quant.quantity)

                    lines.append(f"{lot} -> {numero_adm} : {ac}/{k_two}/{k_seven}/{pesticides} ({qty})\n\n")
                    lines_report.append(f"{lot} -> {numero_adm} : {ac}/{k_two}/{k_seven}/{pesticides} ({qty})\n\n")
                    lines.append("-\n")

                else:
                    lines.append(f"No Lot -> - : -/-/-/- ({round(quant.quantity)})\n\n")
                    lines_report.append(f"No Lot -> - : -/-/-/- ({round(quant.quantity)})\n\n")
                    lines.append("-------------------------------------------------\n")
                    lines_report.append("-\n")
            location.product_lot_info = "\n\n".join(lines) if lines else "No stock"
            location.product_lot_report = "\n\n".join(lines_report) if lines_report else "No stock"

    @api.model
    def cron_recompute_capacity(self):

        locations = self.search([("capacity_max", ">", 0)])
        locations._compute_capacity()