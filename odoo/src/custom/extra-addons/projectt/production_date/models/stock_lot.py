from odoo import fields, models


class ProductionLot(models.Model):
    _inherit = "stock.lot"

    use_production_date = fields.Boolean(related="product_id.use_production_date")
    production_date = fields.Date(string="Production Date")
