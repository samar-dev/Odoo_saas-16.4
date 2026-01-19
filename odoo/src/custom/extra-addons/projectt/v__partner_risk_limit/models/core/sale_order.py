from odoo import fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    x_risk_limit = fields.Float(string="Risque", related="partner_id.x_risk_limit")
    x_current_risk_amount = fields.Float(
        string="Risque actuel", related="partner_id.x_current_risk_amount"
    )
    x_show_risk_limit = fields.Boolean(related="partner_id.x_show_risk_limit")

    def action_confirm(self):
        for order in self:
            partner_id = order.partner_id
            if (
                partner_id.x_current_risk_amount + order.amount_total
                > partner_id.x_risk_limit
                and order.x_show_risk_limit
            ):
                raise ValidationError("Risque client est dépassé")
        res = super(SaleOrder, self).action_confirm()
        return res
