from odoo import fields, models

from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    x_is_sale_allowed = fields.Boolean(
        string="Vente autorisé", compute="_compute_x_is_sale_allowed"
    )
    x_show_block_unpaid_customer = fields.Boolean(
        related="partner_id.x_show_block_unpaid_customer"
    )

    def _compute_x_is_sale_allowed(self):
        for sale in self:
            sale.x_is_sale_allowed = not sale.partner_id.x_customer_blocked

    def action_confirm(self):
        for order in self:
            if (
                order.partner_id.x_customer_blocked
                and order.x_show_block_unpaid_customer
            ):
                raise UserError("Client Bloqué")
        res = super(SaleOrder, self).action_confirm()
        return res
