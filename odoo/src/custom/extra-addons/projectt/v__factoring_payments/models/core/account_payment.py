from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    account_factoring_id = fields.Many2one(comodel_name="account.factoring")
    factoring_id = fields.Many2one(comodel_name="account.factoring")

    def action_add_factoring_payment(self):
        self.ensure_one()
        # we are going to change the receivable account with the factoring account
        # which is not a nice move for odoo and will complain about it.
        # so we told him to let us do it
        self = self.with_context(skip_account_move_synchronization=True)
        factoring_id = self.env["account.factoring"].browse(
            self._context.get("active_id")
        )
        factoring_move_id = factoring_id.factoring_move_id
        debit_line = factoring_move_id.line_ids.filtered_domain(
            [("debit", "=", factoring_id.new_amount)]
        )
        factoring_journal_id = factoring_id.journal_id
        factoring_account_id = factoring_journal_id.default_account_id
        credit_line = self.move_id.line_ids.filtered_domain([("credit", ">", 0)])
        credit_line.account_id = factoring_account_id
        self.action_post()
        (credit_line + debit_line).reconcile()
        self.factoring_id = factoring_id
        total_factoring_payments = sum(
            factoring_id.factoring_payment_ids.mapped("amount")
        )
        if total_factoring_payments >= factoring_id.new_amount:
            factoring_id.state = "done"

    def action_open_factoring_move_entry(self):
        self.ensure_one()
        action = {
            "name": self.factoring_move_id.name,
            "view_mode": "form",
            "res_model": "account.move",
            "type": "ir.actions.act_window",
            "res_id": self.factoring_move_id.id,
            "context": {"create": False},
            "target": "self",
        }
        return action

    @api.ondelete(at_uninstall=False)
    def _delete_factoring_payments(self):
        for record in self:
            if record.account_factoring_id:
                raise ValidationError(
                    _(
                        "This payment belongs to a factoring document %s"
                        % record.account_factoring_id.name
                    )
                )
            # if we delete a factoring payment
            # we must reset the factoring document to pending
            # so the user can pass the payment again
            if record.factoring_id.state == "done":
                record.factoring_id.state = "pending"
