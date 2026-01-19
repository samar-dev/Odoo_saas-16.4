from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _get_computed_taxes(self):
        res = super(AccountMoveLine, self)._get_computed_taxes()
        for line in self:
            move_id = line.move_id
            withholding_tax_id = move_id.withholding_tax_id
            if line.product_id.is_tax_stamp:
                continue
            if move_id.with_withholding and line.product_id:
                res |= withholding_tax_id
        return res
