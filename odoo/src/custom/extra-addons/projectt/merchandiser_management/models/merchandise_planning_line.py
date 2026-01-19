from odoo import fields, models


class MerchandisePlanningLine(models.Model):
    _name = "merchandise.planning.line"
    _description = "Merchandise Planning Line"

    product_id = fields.Many2one("product.product", string="Product")
    barcode = fields.Char(related="product_id.barcode", string="Barcode")
    product_name = fields.Char(related="product_id.name", string="Name")
    last_visit_date = fields.Date(
        string="Visit N-1 Date", related="merchandise_planning_id.last_visit_date"
    )

    stock_out = fields.Boolean(
        default=True,
        string="Non stock-out/Stock-out",
    )

    rupture_date = fields.Date(string="Rupture date")
    quantity = fields.Float(string="Quantity")
    merchandise_planning_id = fields.Many2one("merchandise.planning")
    assortment_id = fields.Many2one(related="merchandise_planning_id.assortment_id")
    store_id = fields.Many2one("res.partner.store", string="Store")
    state = fields.Selection(related="merchandise_planning_id.state")
    start_datetime = fields.Datetime(related="merchandise_planning_id.start_datetime")
    active = fields.Boolean(string="Active", default=True)
