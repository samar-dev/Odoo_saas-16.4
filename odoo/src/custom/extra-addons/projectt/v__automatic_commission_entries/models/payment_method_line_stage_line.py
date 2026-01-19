from odoo import _, fields, models


class PaymentMethodLineStageLine(models.Model):
    _inherit = "payment.method.line.stage.line"

    account_commission_id = fields.Many2one(comodel_name="account.commission")

    def action_display_commissions(self):
        self.ensure_one()
        if not self.account_commission_id:
            self.account_commission_id = self.account_commission_id.create(
                {"payment_method_line_stage_line_id": self.id}
            )
        action = {
            "name": _("Commission"),
            "view_mode": "form",
            "res_model": "account.commission",
            "type": "ir.actions.act_window",
            "res_id": self.account_commission_id.id,
            "context": {"create": False, "delete": False},
            "target": "new",
        }
        return action
