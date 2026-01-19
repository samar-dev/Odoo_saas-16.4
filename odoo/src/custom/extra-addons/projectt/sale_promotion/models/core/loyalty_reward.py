from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class LoyaltyReward(models.Model):
    _inherit = "loyalty.reward"

    promotion_quantity = fields.Float(string=_("Promotion quantity"), required=False)
    product_quantity = fields.Float(
        string=_("Quantity in stock"), related="reward_product_id.qty_available"
    )
    remaining_promotion_quantity = fields.Float(
        string=_("Remaining promotion quantity"),
        compute="_compute_remaining_promotion_quantity",
    )

    @api.onchange("promotion_quantity")
    def onchange_promotion_quantity(self):
        if self.promotion_quantity > self.product_quantity:
            raise ValidationError(
                _("the promotional quantity must be less than the quantity in stock.")
            )

    @api.depends("promotion_quantity", "program_id.coupon_count")
    def _compute_remaining_promotion_quantity(self):
        for record in self:
            record.remaining_promotion_quantity = (
                -1
                if record.promotion_quantity == 0
                else record.promotion_quantity
                - (record.program_id.coupon_count * record.reward_product_qty)
            )
            if record.remaining_promotion_quantity == 0:
                record.program_id.active = False

