from odoo import fields, models
from odoo.exceptions import ValidationError


class AccountPaymentMethodLine(models.Model):
    _inherit = "account.payment.method.line"

    payment_method_line_stage_id = fields.Many2one(
        comodel_name="payment.method.line.stage"
    )

    def open_payment_method_line_stage(self):
        self.ensure_one()
        if not self.payment_method_line_stage_id:
            vals = {"name": self.name}
            if self.payment_type == "inbound":
                vals["inbound_payment_method_line_id"] = self.id
            elif self.payment_type == "outbound":
                vals["outbound_payment_method_line_id"] = self.id

            stages = self.payment_method_id.stage_ids.mapped(
                lambda stage: {
                    "sequence": stage.sequence,
                    "name": stage.name,
                    "type": stage.type,
                }
            )
            if not stages:
                raise ValidationError(
                    "Veuillez d'abord définir les étapes de la méthode de paiement"
                )
            self.payment_method_line_stage_id = self.env[
                "payment.method.line.stage"
            ].create(vals)
            for stage in stages:
                self.payment_method_line_stage_id.payment_method_line_stage_line_ids = [
                    [0, 0, stage]
                ]
        action = {
            "name": self.name,
            "view_mode": "form",
            "res_model": "payment.method.line.stage",
            "type": "ir.actions.act_window",
            "res_id": self.payment_method_line_stage_id.id,
            "target": "new",
        }
        return action
