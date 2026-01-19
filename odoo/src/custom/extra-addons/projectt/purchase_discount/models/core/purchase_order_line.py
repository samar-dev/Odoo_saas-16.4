from odoo import models, fields, api, _


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    pol_discount = fields.Float(string=_("Disc.%"))

    @api.depends("product_qty", "price_unit", "pol_discount", "taxes_id")
    def _compute_amount(self):
        super(PurchaseOrderLine, self)._compute_amount()

    def _convert_to_tax_base_line_dict(self):
        return super(
            PurchaseOrderLine, self.with_context(discount=self.pol_discount)
        )._convert_to_tax_base_line_dict()

    def _prepare_account_move_line(self, move=False):
        res = super(PurchaseOrderLine, self)._prepare_account_move_line()
        res["discount"] = self.pol_discount
        return res
