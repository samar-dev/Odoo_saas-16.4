from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tests.common import Form


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    with_bank_commission = fields.Boolean(
        string=_("With Bank Commission"), default=False
    )
    commission_account_id = fields.Many2one(
        comodel_name="account.account", string=_("Commission Account")
    )
    commission_label = fields.Char(string=_("Commission Label"))
    commission_amount = fields.Monetary(string=_("Commission Amount"))

    @api.constrains("commission_amount")
    def _check_commission_amount(self):
        if self.commission_amount < 0:
            raise ValidationError(_("Commission amount can't be negative"))

    @api.onchange('commission_account_id')
    def write_commission_label(self):
        self.commission_label = self.commission_account_id.name

    @api.onchange('writeoff_account_id')
    def write_off_label(self):
        self.writeoff_label = self.writeoff_account_id.name

    def _create_payments(self):
        res = super(AccountPaymentRegister, self)._create_payments()
        commission_amount = self.commission_amount
        commission_label = self.commission_label
        commission_account_id = self.commission_account_id
        payment_difference = self.payment_difference
        # commission amount won't be visible in the view
        # unless there is a payment difference
        # if we got a payment difference and the user let the amount null
        # we let odoo do its job by creating a single write-off line
        if commission_amount:
            for payment_id in res:

                conversion_rate = self.env['res.currency']._get_conversion_rate(
                    res.currency_id,
                    res.company_id.currency_id,
                    res.company_id,
                    res.date,
                )
                commission_amount_tnd = self.company_id.currency_id.round(commission_amount * conversion_rate)
                move_id = payment_id.move_id
                # reset move_id/payment to draft, so we can modify the line
                move_id.button_draft()
                line_to_edit = move_id.line_ids.filtered(
                    lambda line: line.account_id == self.writeoff_account_id
                )
                line_index = list(move_id.line_ids).index(line_to_edit)
                with Form(
                        move_id.with_context(skip_account_move_synchronization=True)
                ) as move:
                    line = move.line_ids.edit(line_index)
                    if payment_difference < 0:
                        if payment_id.payment_type == "inbound":
                            line.credit += commission_amount_tnd
                        else:
                            line.credit = commission_amount_tnd - line.debit
                            line.debit = 0
                    else:
                        if payment_id.payment_type == "inbound":
                            line.debit -= commission_amount_tnd
                        else:
                            line.credit += commission_amount_tnd
                    line.save()
                    commission_line = move.line_ids.new()
                    commission_line.account_id = commission_account_id
                    commission_line.debit = commission_amount_tnd
                    commission_line.name = commission_label
                    commission_line.amount_currency: commission_amount
                    commission_line.save()
                payment_id.x_skip_account_move_sync = True
                payment_id.action_post()

        return res
