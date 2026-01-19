from odoo import fields, models


class PaymentMethodLineStage(models.Model):
    _name = "payment.method.line.stage"

    name = fields.Char(string="Nom", required=True, readonly=True)
    inbound_payment_method_line_id = fields.Many2one(
        comodel_name="account.payment.method.line"
    )
    outbound_payment_method_line_id = fields.Many2one(
        comodel_name="account.payment.method.line"
    )
    payment_method_line_stage_line_ids = fields.One2many(
        comodel_name="payment.method.line.stage.line",
        inverse_name="payment_method_line_stage_id",
    )
    hide_banknote_type = fields.Boolean(compute="_compute_hide_banknote_type")

    def _compute_hide_banknote_type(self):
        for record in self:
            # line will be either inbound or outbound can't be both at the same time
            payment_method_code = (
                record.inbound_payment_method_line_id
                + record.outbound_payment_method_line_id
            ).code
            record.hide_banknote_type = payment_method_code != "v-banknote"
