from odoo import api, fields, models
from odoo.exceptions import ValidationError


class RegularizeByCertificateWiz(models.TransientModel):
    _name = "regularize.by.certificate.wiz"

    date = fields.Date(
        string="Date", default=lambda self: fields.date.today(), required=True
    )
    certificate_name = fields.Char()
    certificate_file = fields.Binary(string="Attestation", required=True)

    @api.constrains("date")
    def _check_date(self):
        if self.date > fields.Date.today():
            raise ValidationError(
                "La date doit être inférieure ou égale à la date du jour"
            )

    def button_call_regularize(self):
        self.ensure_one()
        payment_id = self.env["account.payment"].browse(self._context.get("active_id"))
        payment_id.certificate_file = self.certificate_file
        payment_id.certificate_name = self.certificate_name
        available_stages = payment_id._get_available_stages()
        in_bank = available_stages.filtered_domain([("type", "=", "in_bank")])
        unpaid = available_stages.filtered_domain([("type", "=", "unpaid")])
        bank_account = in_bank.account_id
        unpaid_account = unpaid.account_id
        payment_id.with_context(entry_date=self.date)._create_journal_entry(
            credit_account=unpaid_account, debit_account=bank_account
        )
        payment_id.write(
            {
                "certificate_file": self.certificate_file,
                "certificate_name": self.certificate_name,
                "x_new_stage_id": in_bank,
                "is_unpaid": "fixed",
                "is_paid": True,
            }
        )
        if payment_id.is_prior_notice == "yes":
            payment_id.is_prior_notice = "fixed"
        # check if the customer still have unpaid payments
        # or prior_notice payments
        payment_domain = [
            ("partner_id", "=", payment_id.partner_id.id),
            ("payment_type", "=", "inbound"),
            ("partner_type", "=", "customer"),
            ("company_id", "=", self.env.company.id),
            ("state", "=", "posted"),
            "|",
            ("is_prior_notice", "=", "yes"),
            ("is_unpaid", "=", "yes"),
        ]
        payments_to_fix = payment_id.search(payment_domain)
        if not payments_to_fix:
            message = f"Déblocage suite régularisation impayé {payment_id.name}"
            if payment_id.transaction_number:
                message += (
                    f" - {payment_id.payment_method_name} "
                    f"{payment_id.transaction_number} {payment_id.due_date}"
                )
            payment_id._set_customer_blocked_state(message=message, state="unblocked")
