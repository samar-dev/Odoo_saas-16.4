from odoo import fields, models


class LoyaltyProgram(models.Model):
    _inherit = "loyalty.program"

    vendor_id = fields.Many2one(
        comodel_name="res.users", string="Vendor", required=False
    )
    partner_id = fields.Many2many(
        comodel_name="res.partner",
        string="Customer",
        readonly=False,
        tracking=1,
        domain="[('company_id', 'in', (False, company_id))]",
    )
