from odoo import fields, models


class AccountCommission(models.Model):
    _name = "account.commission"

    account_commission_line_ids = fields.One2many(
        comodel_name="account.commission.line", inverse_name="account_commission_id"
    )
    payment_method_line_stage_line_id = fields.Many2one(
        comodel_name="payment.method.line.stage.line"
    )
