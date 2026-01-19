from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def write(self, vals):
        res = super(AccountMoveLine, self).write(vals)
        if "full_reconcile_id" in vals:
            # the bank statement will be reconciled with the main move_id
            # or with one of our custom x_move_ids
            move_ids = self.move_id.filtered(
                lambda move: move.x_payment_id
            ) or self.move_id.filtered(lambda move: move.payment_id)
            payment_ids = move_ids.x_payment_id or move_ids.payment_id
            payment_ids._compute_stat_buttons_from_reconciliation()
            for payment_id in payment_ids:
                next_stage_id = payment_id._get_next_stage_id()
                if (
                    next_stage_id.type == "in_bank"
                    and next_stage_id.with_bank_statement
                    and payment_id.reconciled_statement_lines_count != 0
                ):
                    payment_id._action_move_to_next_stage()
        return res
