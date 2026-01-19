from odoo import fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    x_credit_limit = fields.Float(string="Encours", related="partner_id.x_credit_limit")
    x_current_outstanding_amount = fields.Float(
        string="Encours actuel", related="partner_id.x_current_outstanding_amount"
    )
    x_show_credit_limit = fields.Boolean(related="partner_id.x_show_credit_limit")

    def action_confirm(self):
        for order in self:
            partner_id = order.partner_id
            if (
                partner_id.x_current_outstanding_amount + order.amount_total
                > partner_id.x_credit_limit
                and order.x_show_credit_limit
            ):
                raise ValidationError("L'encours client est dépassé")
        res = super(SaleOrder, self).action_confirm()
        return res
