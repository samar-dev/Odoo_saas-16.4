from odoo import models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_confirm(self):
        for picking in self:
            if picking.partner_id.x_customer_blocked:
                raise UserError("Client Bloqué")
        res = super(StockPicking, self).action_confirm()
        return res

    def button_validate(self):
        for picking in self:
            if (
                picking.partner_id.x_customer_blocked
                and picking.partner_id.x_show_block_unpaid_customer
            ):
                raise UserError("Client Bloqué")
        res = super(StockPicking, self).button_validate()
        return res
