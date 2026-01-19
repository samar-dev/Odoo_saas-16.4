from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    is_reward_applied = fields.Boolean("Is reward applied", default=False)
