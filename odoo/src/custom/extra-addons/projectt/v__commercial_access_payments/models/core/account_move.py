from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        if self.env.user.has_group(
            "v__commercial_access_payments.group_special_access_payment"
        ):
            self = self.sudo()
        return super(AccountMove, self).action_post()
