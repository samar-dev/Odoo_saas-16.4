from odoo import fields, models, api


class StockLandedCost(models.Model):
    _inherit = "stock.landed.cost"

    @api.onchange("picking_ids")
    def _onchange_deleviry_id(self):
        for recod in self:
            for line in recod.cost_lines:
                line.account_id = line.product_id.property_account_expense_id  # marwan
