from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.depends("company_id", "invoice_filter_type_domain")
    def _compute_suitable_journal_ids(self):
        super(AccountMove, self)._compute_suitable_journal_ids()
        for record in self:
            record.suitable_journal_ids |= self.env["account.journal"].search(
                [("x_type", "=", 'withholding')]
            )
