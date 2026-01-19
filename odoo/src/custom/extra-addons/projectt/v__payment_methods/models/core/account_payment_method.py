from odoo import api, fields, models


class AccountPaymentMethod(models.Model):
    _inherit = "account.payment.method"

    stage_ids = fields.One2many(
        comodel_name="account.payment.method.stage", inverse_name="payment_method_id"
    )

    @api.model
    def _get_payment_method_information(self):
        res = super(AccountPaymentMethod, self)._get_payment_method_information()
        payment_methods = ("v-check", "v-cash", "v-banknote", "v-transfer")
        for payment_method in payment_methods:
            res[payment_method] = {
                "mode": "multi",
                "domain": [("type", "in", ("bank", "cash"))],
            }
        return res
