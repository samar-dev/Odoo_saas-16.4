from odoo import fields, models


class ConcurrentLine(models.Model):
    _name = "concurrent.line"
    _description = "Concurrent Line"

    concurrent_name = fields.Char(string="Concurrent")
    promo = fields.Selection(
        [("new_referencing", "New referencing"), ("promotion", "Promotion")],
        string="Promo",
    )
    note = fields.Text(string="Note")
    merchandise_planning_id = fields.Many2one("merchandise.planning")
