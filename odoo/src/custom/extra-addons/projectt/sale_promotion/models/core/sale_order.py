from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_reward_line_values(self, reward, coupon, **kwargs):
        self.ensure_one()
        self = self.with_context(lang=self.partner_id.lang)
        reward = reward.with_context(lang=self.partner_id.lang)
        if reward.reward_type == "discount":
            line = self.order_line.filtered(
                lambda line: not line.is_reward_applied
                and reward.discount_line_product_id
            )
            line[0].discount += reward.discount
            line[0].write({"is_reward_applied": True})
            return {}
        else:
            return super(SaleOrder, self)._get_reward_line_values(
                reward, coupon, **kwargs
            )

    def _get_claimable_rewards(self, forced_coupons=None):
        result = super(SaleOrder, self)._get_claimable_rewards(forced_coupons)
        # Filtering the dictionary
        filtered_result = {
            k: v
            for k, v in result.items()
            if not (
                k.program_id.partner_id
                and self.partner_id
                and self.partner_id not in k.program_id.partner_id
            )
        }
        # Update the original result dictionary
        result = filtered_result
        return result
