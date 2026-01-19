from datetime import datetime
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class CreatePurchaseOrderWizard(models.TransientModel):
    _name = "wizard.create.purchase"

    sale_id = fields.Many2one("sale.order")
    partner_id = fields.Many2one("res.partner", "Select Vendor", required=True)
    product_quantity_line_ids = fields.One2many(
        "product.quantity.line", "create_purchase_wizard_id"
    )

    @api.onchange("sale_id")
    def onchange_sale_id(self):
        data = []
        for line in self.sale_id.order_line:
            data.append(
                (
                    0,
                    0,
                    {
                        "product_id": line.product_id.id,
                        "name": line.name,
                        "qty": line.product_uom_qty,
                        "max_qty": line.product_uom_qty,
                        "price_unit": line.price_unit,
                    },
                )
            )
        self.product_quantity_line_ids = data
        self.partner_id = self.sale_id.partner_id

    def create_purchase_order(self):
        data = []
        [
            data.append(
                (
                    0,
                    0,
                    {
                        "product_id": line.product_id.id,
                        "name": line.name if line.name else line.product_id.name,
                        "product_qty": line.qty,
                        "price_unit": line.price_unit,
                    },
                )
            )
            for line in self.product_quantity_line_ids
            if line.qty > 0
        ]
        if len(data) > 0:
            vals = {
                "partner_id": self.partner_id.id,
                "date_order": datetime.now(),
                "order_line": data,
                "sale_id": self.sale_id.id,
            }
            self.sale_id.purchase_id = self.env["purchase.order"].create(vals).id
        else:
            raise UserError(
                _("Quantity should be provided for atleast one product !!!")
            )


class ProductQuantityLine(models.TransientModel):
    _name = "product.quantity.line"

    name = fields.Char("Description")
    product_id = fields.Many2one("product.product", "Product")
    qty = fields.Float("Purchase Quantity", required=True)
    max_qty = fields.Float()
    price_unit = fields.Float()
    create_purchase_wizard_id = fields.Many2one("wizard.create.purchase")

    @api.onchange("qty")
    def onchange_qty(self):
        if self.qty > self.max_qty:
            raise UserError(
                _("Purchase quantity cannot be greater than requested quantity !!!")
            )
