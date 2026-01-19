from odoo import fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    x_skip_account_move_sync = fields.Boolean(default=False)

    def _synchronize_from_moves(self, changed_fields):
        # used to bypass account checking because we have two writeoff accounts
        if any(self.mapped("x_skip_account_move_sync")):
            return
        return super(AccountPayment, self)._synchronize_from_moves(changed_fields)

    def _synchronize_to_moves(self, changed_fields):
        # used to bypass account checking because we have two writeoff accounts
        if any(self.mapped("x_skip_account_move_sync")):
            return
        return super(AccountPayment, self)._synchronize_to_moves(changed_fields)
