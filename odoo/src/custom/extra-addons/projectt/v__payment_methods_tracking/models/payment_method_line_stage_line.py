from odoo import api, fields, models, _


class PaymentMethodLineStageLine(models.Model):
    _name = "payment.method.line.stage.line"
    _order = "sequence asc, id asc"

    sequence = fields.Integer(default=1, required=True)
    name = fields.Char(string=_("Name"), required=True)
    payment_method_line_stage_id = fields.Many2one(
        comodel_name="payment.method.line.stage"
    )
    payment_method_line_id = fields.Many2one(
        comodel_name="account.payment.method.line",
        compute="_compute_payment_method_line_id",
        store=True,
    )
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
    with_bank_statement = fields.Boolean(string="Avec Relevé Bancaire")
    account_id = fields.Many2one(string="Compte", comodel_name="account.account")
    banknote_type = fields.Selection(
        string="Type d'effet",
        selection=[("at_due_date", "Encaissement"), ("before_due_date", "Escompte")],
        copy=False,
    )
    with_journal_entry = fields.Boolean(string="Avec Écriture", default=True)

    @api.depends("payment_method_line_stage_id")
    def _compute_payment_method_line_id(self):
        for record in self:
            record.payment_method_line_id = (
                record.payment_method_line_stage_id.inbound_payment_method_line_id
                or record.payment_method_line_stage_id.outbound_payment_method_line_id
            )
