from odoo import models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def action_post(self):
        if self.env.user.has_group(
            "v__commercial_access_payments.group_special_access_payment"
        ):
            self = self.sudo()
        return super(AccountPayment, self).action_post()
