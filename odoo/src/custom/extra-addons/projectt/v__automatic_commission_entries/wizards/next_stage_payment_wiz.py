from odoo import fields, models


class NextStagePaymentWizard(models.TransientModel):
    _inherit = "next.stage.payment.wiz"

    show_commission_table = fields.Boolean(default=False)
    next_stage_payment_commission_line_ids = fields.One2many(
        comodel_name="next.stage.payment.commission.line",
        inverse_name="next_stage_payment_wiz_id",
    )

    def button_call_next_stage(self):
        active_ids = self._context.get("active_ids")
        payment_ids = self.env["account.payment"].browse(active_ids)
        for payment_id in payment_ids:
            for line in self.next_stage_payment_commission_line_ids:
                if not line.value:
                    continue
                payment_id.account_payment_commission_ids = [
                    (
                        0,
                        0,
                        {
                            "name": line.name,
                            "label": line.label,
                            "value": line.value,
                            "value_type": line.value_type,
                            "account_id": line.account_id.id,
                        },
                    )
                ]
        res = super(NextStagePaymentWizard, self).button_call_next_stage()
        return res
