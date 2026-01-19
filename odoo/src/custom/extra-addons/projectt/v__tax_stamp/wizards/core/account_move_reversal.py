from odoo import models, fields


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    refund_tax_stamp = fields.Boolean(string="Avec Timbre Fiscal")

    def _prepare_default_reversal(self, move):
        res = super(AccountMoveReversal, self)._prepare_default_reversal(move)
        res.update({"refund_tax_stamp": self.refund_tax_stamp})
        return res
