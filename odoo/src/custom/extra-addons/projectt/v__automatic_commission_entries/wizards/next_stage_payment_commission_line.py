from odoo import _, fields, models


class NextStagePaymentCommissionLine(models.TransientModel):
    _name = "next.stage.payment.commission.line"

    next_stage_payment_wiz_id = fields.Many2one(comodel_name="next.stage.payment.wiz")
    name = fields.Char(string=_("Name"), required=True, readonly=True)
    label = fields.Char(string=_("Label"), required=True, readonly=True)
    value_type = fields.Selection(
        string=_("Value Type"),
        selection=[("amount", _("Amount")), ("percentage", _("Percentage"))],
        required=True,
        default="variable",
    )
    value = fields.Float(string=_("Value"), default=0, required=True)
    account_id = fields.Many2one(
        string=_("Account"),
        comodel_name="account.account",
        required=True,
        readonly=True,
    )
