from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    scale_id = fields.Many2one("scale.reader", string="Scale")
