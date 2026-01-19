from odoo import api, exceptions, models


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    @api.onchange("payment_method_line_id")
    def _check_for_stage_ids(self):
        # Overridden
        if self.payment_method_code in (
            "v-check",
            "v-banknote",
            "v-cash",
            "v-transfer",
        ):
            if not self.payment_method_line_id.payment_method_line_stage_id:
                raise exceptions.ValidationError(
                    "Veuillez d'abord configurer vos modes de paiement dans le journal"
                )
