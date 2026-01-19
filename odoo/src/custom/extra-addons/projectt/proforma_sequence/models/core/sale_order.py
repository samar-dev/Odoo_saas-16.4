from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    x_seq_proforma_invoice = fields.Char(
        string="Pro-forma invoice sequence", readonly=True
    )

    @api.model
    def create(self, vals):
        sales = super(SaleOrder, self).create(vals)
        for sale in sales:
            if sale and sale.x_customer_type == "export":
                sale.x_seq_proforma_invoice = self.env["ir.sequence"].next_by_code(
                    "proforma.invoice"
                )
        return sales
