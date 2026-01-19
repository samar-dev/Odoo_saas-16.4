from odoo import models


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    def _reconcile_payments(self, to_process, edit_mode=False):
        for vals in to_process:
            payment_id = vals["payment"]
            # get the payment being replaced
            original_payment_ids = self.env["account.payment"].browse(
                self._context.get("original_payment_ids", [])
            )
            replacement_amount = payment_id.amount
            for original_payment_id in original_payment_ids.sorted(
                lambda pay: (pay.amount, pay.id)
            ):
                # no need to add it to the original payment as a replacement
                if replacement_amount == 0:
                    continue

                amount_due = (
                    original_payment_id.amount - original_payment_id.replaced_amount
                )

                # check if the customer still have unpaid payments
                # or prior_notice payments
                payment_domain = [
                    ("partner_id", "=", original_payment_id.partner_id.id),
                    ("payment_type", "=", "inbound"),
                    ("partner_type", "=", "customer"),
                    ("company_id", "=", self.env.company.id),
                    ("state", "in", ("cancel", "posted")),
                    "|",
                    ("is_prior_notice", "=", "yes"),
                    ("is_unpaid", "=", "yes"),
                ]
                if replacement_amount >= amount_due:
                    original_payment_id.replaced_amount += amount_due
                    replacement_amount -= amount_due
                else:
                    original_payment_id.replaced_amount += replacement_amount
                    replacement_amount = 0

                payment_id.original_payment_ids |= original_payment_id
                original_payment_id.replacement_payment_ids |= payment_id
                if original_payment_id.replaced_amount >= original_payment_id.amount:
                    write_vals = {"is_replaced": True}
                    original_payment_id._set_payment_state(write_vals=write_vals, state="yes")
                    payments_to_fix = payment_id.search(payment_domain)
                    if not payments_to_fix:
                        message = (
                            f"Déblocage suite régularisation impayé {payment_id.name}"
                        )
                        if payment_id.transaction_number:
                            message += (
                                f" - {payment_id.payment_method_name} "
                                f"{payment_id.transaction_number} {payment_id.due_date}"
                            )
                        payment_id._set_customer_blocked_state(
                            message=message, state="unblocked"
                        )

        return super(AccountPaymentRegister, self)._reconcile_payments(
            to_process, edit_mode
        )
