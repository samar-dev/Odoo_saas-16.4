from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    customer_type = fields.Selection(
        related="partner_id.x_customer_type", string="Customer type"
    )
    discharge_port = fields.Char(string=_("Discharge port"))
    orginal_print = fields.Boolean(string="Ajuster le prix")
    loading_port = fields.Char(string=_("Loading port"))
    shipping_date = fields.Date(string=_("Shipping date"))
    free_detention_days = fields.Integer(string=_("Free detention days"))

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        self.discharge_port = self.loading_port = self.shipping_date = (
            self.free_detention_days
        ) = False

    @api.onchange("order_line")
    def _onchange_order_line(self):
        for record in self:
            gateg_ids = record.order_line.filtered(
                lambda line: line.product_id.categ_id.other_operation == True
            )
        if gateg_ids:
            record.picking_type_id = gateg_ids[0].product_id.categ_id.operation

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        if res:
            # Assuming you want to check the sale order itself, not a list
            if self.partner_id.x_customer_type in [
                "prospect_client",
                "prospect_fournisseur",
            ]:
                raise ValidationError(
                    _(
                        "Action ne peut pas être effectuée car le type de client est défini sur 'Prospect Client' ou 'Prospect Fournisseur'. Veuillez mettre à jour le type de client avant de continuer."
                    )
                )
            else:
                if self.orginal_print:
                    for line in self.order_line:
                        if line.display_type not in ["line_note", "line_section"]:
                            line.price_unit = round(
                                line.price_total / line.product_qty, 3
                            )
                            line.taxes_id = [(5, 0, 0)]
        return res

    def recompute_price(self):

        if self.orginal_print:
            for line in self.order_line:
                if line.display_type not in ["line_note", "line_section"]:
                    line.price_unit = round(line.price_total / line.product_qty, 3)
                    line.taxes_id = [(5, 0, 0)]
