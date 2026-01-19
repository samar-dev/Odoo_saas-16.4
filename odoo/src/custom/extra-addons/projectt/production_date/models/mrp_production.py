from odoo import models
from datetime import datetime


class ManufacturingOrder(models.Model):
    _inherit = "mrp.production"

    def write(self, vals):
        if (
            "lot_producing_id" in vals
            and self.product_id.tracking in ("lot", "serial")
            and self.product_id.use_production_date
        ):
            self.env["stock.lot"].browse(
                vals["lot_producing_id"]
            ).production_date = datetime.today().date()
        return super().write(vals)
