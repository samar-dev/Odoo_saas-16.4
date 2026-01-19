from odoo import api, fields, models
from odoo.tests.common import Form


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    hide_stamp_zero_taxed = fields.Boolean(
        compute="_compute_hide_stamp_zero_taxed", store=True
    )

    is_tax_stamp = fields.Boolean(compute="_compute_is_tax_stamp")

    def _compute_is_tax_stamp(self):
        for line in self:
            line.is_tax_stamp = line.product_id.is_tax_stamp

    @api.depends("account_id")
    def _compute_hide_stamp_zero_taxed(self):
        for line in self:
            line.hide_stamp_zero_taxed = False
            product_id = line.product_id
            if product_id.is_tax_stamp and line.credit == line.debit == 0:
                line.hide_stamp_zero_taxed = True
