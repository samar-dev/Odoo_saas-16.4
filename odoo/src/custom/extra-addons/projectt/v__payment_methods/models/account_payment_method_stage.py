from odoo import _, fields, models


class PaymentMethodStage(models.Model):
    _name = "account.payment.method.stage"
    _description = "Payment Method Stage"
    _order = "sequence asc, id asc"

    name = fields.Char(string=_("Name"), required=True)
    type = fields.Selection(
        string="Type d'étape",
        selection=[
            ("must_be_sent", "Doit être envoyé"),
            ("reconcile", "Rapprochement"),
            ("in_bank", "En Banque"),
            ("butterfly", "Papillon"),
            ("prior_notice", "Préavis"),
            ("unpaid", "Impayé"),
        ],
    )
    sequence = fields.Integer(default=1, required=True)
    payment_method_id = fields.Many2one(
        string=_("Payment Method"), comodel_name="account.payment.method"
    )
