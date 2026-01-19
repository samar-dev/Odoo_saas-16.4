from odoo import api, fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    show_commission_page = fields.Boolean(compute="_compute_show_commission_page")
    account_payment_commission_ids = fields.One2many(
        comodel_name="account.payment.commission", inverse_name="payment_id"
    )

    @api.depends("account_payment_commission_ids")
    def _compute_show_commission_page(self):
        for record in self:
            record.show_commission_page = bool(record.account_payment_commission_ids)

    def _call_next_stage_payment_wiz(self, callback):
        res = super(AccountPayment, self)._call_next_stage_payment_wiz(callback)
        # get the current stage to check
        # if it is configured to have a commission or not
        account_commission_id = self.x_new_stage_id.account_commission_id
        commission_line_ids = account_commission_id.account_commission_line_ids
        if commission_line_ids:
            wizard = self.env["next.stage.payment.wiz"].create(
                {"show_commission_table": True}
            )
            res["res_id"] = wizard.id
            values = commission_line_ids.mapped(
                lambda line: {
                    "name": line.name,
                    "label": line.label,
                    "next_stage_payment_wiz_id": wizard.id,
                    "value": line.value,
                    "value_type": line.value_type,
                    "account_id": line.account_id.id,
                }
            )
            wizard.next_stage_payment_commission_line_ids.create(values)

        return res

    def action_move_to_next_stage(self):
        for payment in self:
            current_stage = payment.x_new_stage_id
            if (
                current_stage.account_commission_id.account_commission_line_ids
                and payment.account_payment_commission_ids
            ):
                for commission_line in payment.account_payment_commission_ids:
                    default_line_name = "".join(
                        x[1] for x in self._get_aml_default_display_name_list()
                    )
                    label = f"{commission_line.label} - {default_line_name}"
                    # amount can be a raw value amount or a percentage
                    amount = (
                        commission_line.value
                        if commission_line.value_type == "amount"
                        else payment.amount * (commission_line.value / 100)
                    )
                    credit_account = payment.destination_journal_id.default_account_id
                    debit_account = commission_line.account_id
                    # if payment is for supplier we inverse the accounts
                    # because the credit account in inbound
                    # will become debit account in outbound
                    if (
                        payment.payment_type == "outbound"
                        and payment.partner_type == "supplier"
                    ):
                        credit_account, debit_account = debit_account, credit_account
                    payment._create_journal_entry(
                        credit_account=credit_account,
                        debit_account=debit_account,
                        amount=amount,
                        label=label,
                    )
        res = super(AccountPayment, self).action_move_to_next_stage()
        return res
