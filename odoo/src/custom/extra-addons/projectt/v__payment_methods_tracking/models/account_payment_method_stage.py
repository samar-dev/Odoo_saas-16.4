from odoo import fields, models


class PaymentMethodStage(models.Model):
    _inherit = "account.payment.method.stage"

    account_id = fields.Many2one(
        string="Compte Comptable", comodel_name="account.account", required=True
    )
