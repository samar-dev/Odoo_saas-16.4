from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    price_blocked = fields.Boolean(string="Price Blocked", default=False)

    def button_confirm(self):
        for order in self:
            if not order.price_blocked:
                continue

            problematic_line = next(
                (
                    line
                    for line in order.order_line
                    if line.product_id.standard_price
                       and abs(line.price_unit - line.product_id.standard_price)
                       / line.product_id.standard_price
                       > 0.2
                ),
                None,
            )

            if problematic_line:
                raise UserError(
                    _(
                        "Le prix est trop différent du coût du produit pour l'article '%s'. Veuillez contacter votre administrateur."
                    )
                    % problematic_line.product_id.display_name
                )

        return super().button_confirm()

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for order in res:
            for line in order.order_line:
                cost = line.product_id.standard_price
                price = line.price_unit
                if cost and abs(price - cost) / cost > 0.2:
                    order.price_blocked = True
        return res  # <-- Manquant

    def admin_confirm(self):
        allowed_user_ids = [
            2, 41, 35
        ]  # Remplacez 2 par l'ID de l'utilisateur autorisé (ou plusieurs si besoin)

        if self.env.uid not in allowed_user_ids:
            raise UserError(
                _(
                    "Vous n'êtes pas autorisé à contourner le blocage des prix. Veuillez contacter l'administrateur."
                )
            )

        for order in self:
            order.price_blocked = False
        return super().button_confirm()
