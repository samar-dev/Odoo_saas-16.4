from odoo import fields, models, api


class ProductCategory(models.Model):
    _inherit = "product.category"

    property_account_landed_id = fields.Many2one(
        "account.account",
        company_dependent=True,
        string="Landed Cost",
        help="used for landed cost transaction",
    )
