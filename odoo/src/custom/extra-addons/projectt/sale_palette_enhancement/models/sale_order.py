from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_print_pallet_report(self):
        self.ensure_one()
        return self.env.ref('sale_custom_reports.sale_pallets_report_pdf').report_action(self.partner_id)

