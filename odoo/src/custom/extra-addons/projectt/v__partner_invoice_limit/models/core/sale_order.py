from odoo import fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    x_invoice_limit = fields.Integer(
        string="Plafonds Facture", related="partner_id.x_invoice_limit"
    )
    x_current_invoice_limit = fields.Integer(
        string="Facture non payée", related="partner_id.x_current_invoice_limit"
    )
    x_show_invoice_limit = fields.Boolean(related="partner_id.x_show_invoice_limit")

    def action_confirm(self):
        for order in self:
            partner_id = order.partner_id
            if (
                partner_id.x_current_invoice_limit >= partner_id.x_invoice_limit
                and order.x_show_invoice_limit
            ):
                raise ValidationError("Les factures impayées ont atteint le plafond")
        res = super(SaleOrder, self).action_confirm()
        return res
