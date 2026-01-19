from odoo import api, exceptions, models, fields
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare
import logging

_logger = logging.getLogger(__name__)


class AccountBatchPayment(models.Model):
    _inherit = "account.batch.payment"

    x_banknote_type = fields.Selection(
        string="Type d'effet",
        selection=[("at_due_date", "Encaissement"), ("before_due_date", "Escompte")],
        copy=False,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    journal_id = fields.Many2one(string="Source", comodel_name="account.journal")
    destination_journal_id = fields.Many2one(
        string="Banque",
        comodel_name="account.journal",
        copy=False,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    hide_destination_journal = fields.Boolean(
        compute="_compute_hide_destination_journal"
    )
    external_ref = fields.Char(
        string="Référence du bordereau",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    move_to_next_stage = fields.Boolean(
        string="Passer à l'étape suivante",
        default=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    delivered_by = fields.Char(string="Remis par")

    def _compute_hide_destination_journal(self):
        for record in self:
            record.hide_destination_journal = (
                    record.state != "draft"
                    and record.journal_id == record.destination_journal_id
            )

    @api.onchange("destination_journal_id")
    def onchange_destionation_journal_id(self):
        if (
                self.destination_journal_id.x_type == "to_be_cashed"
                and self.journal_id.x_type == "chest"
        ):
            self.move_to_next_stage = False

    # @api.onchange("x_banknote_type")
    # def _onchange_x_banknote_type(self):
    #     if self.x_banknote_type == "at_due_date":
    #         payment_after_today = self.payment_ids.filtered_domain(
    #             [("due_date", ">", fields.date.today())]
    #         )
    #         msg = "Certains traites ont une date d'échéance supérieure à aujourd'hui"
    #         if payment_after_today:
    #             raise UserError(msg)
    #     elif self.x_banknote_type == "before_due_date":
    #         payment_before_today = self.payment_ids.filtered_domain(
    #             [("due_date", "<=", fields.date.today())]
    #         )
    #         msg = (
    #             "Certains traites ont une date d'échéance "
    #             "inférieure ou égale à aujourd'hui"
    #         )
    #         if payment_before_today:
    #             raise UserError(msg)

    @api.constrains("batch_type", "journal_id", "payment_ids")
    def _check_payments_constrains(self):
        res = super(AccountBatchPayment, self)._check_payments_constrains()
        for batch in self.filtered_domain([("state", "=", "draft")]):
            payment_ids = batch.payment_ids.filtered(
                lambda payment: payment._get_next_stage_id().type != "must_be_sent"
            )
            msg = "Le paiement doit être à l'étape où nous devons l'envoyer à la banque"
            if payment_ids:
                raise exceptions.ValidationError(msg)
        return res

    def validate_batch_button(self):
        if self.payment_method_code == "v-banknote" and not self.x_banknote_type:
            raise exceptions.ValidationError(
                "Le type d'effet est requis pour continuer"
            )
        if not self.external_ref:
            raise exceptions.ValidationError(
                "La référence du bordereau est obligatoire pour procéder"
            )

        res = super(AccountBatchPayment, self).validate_batch_button()
        # the error returned by odoo is expected but is not a fatal error is a warning
        # we skip it only in this situation
        if res and self.journal_id.x_type == "to_be_cashed":
            self.payment_ids.mark_as_sent()
            res = None

        # Move payments to next stage
        self.payment_ids.with_context(
            do_not_call_wizard=True, entry_date=self.date
        ).action_move_to_next_stage()

        for payment in self.payment_ids:
            bank_payment = self.with_context(created_from_wizard=True)._clone_payment(payment)

            available_stages = bank_payment._get_available_stages()
            second_stage = bank_payment._get_next_stage_id(stage_id=available_stages[0])

            credit_account = bank_payment.payment_method_line_id.payment_account_id
            debit_account = second_stage.account_id
            desired_account = credit_account

            if bank_payment.payment_type == "outbound":
                credit_account, debit_account = debit_account, credit_account
                desired_account = debit_account

            move = bank_payment.move_id
            if not move:
                raise exceptions.UserError(
                    f"The bank payment {bank_payment.name} has no accounting move yet. Cannot balance."
                )
            # Reset move to draft if needed
            if move.state != 'draft':
                move.button_draft()
            # --- Safe reconciliation handling ---
            reconciled_lines = move.line_ids.filtered('reconciled')
            # Filter out lines to keep
            lines_to_keep = move.line_ids.filtered(lambda l: l.account_id.id != 4715)
            move_lines_data = [{
                'name': line.name,
                'account_id': line.account_id.id,
                'debit': line.debit,
                'credit': line.credit,
            } for line in lines_to_keep]

            # Balance the move
            total_debit = sum(l['debit'] for l in move_lines_data)
            total_credit = sum(l['credit'] for l in move_lines_data)
            difference = total_debit - total_credit

            if abs(difference) > 0.0001:

                if reconciled_lines:
                    reconciled_lines.remove_move_reconcile()
                    _logger.info("Removed reconciliation for move %s to adjust lines", move.name)

                remaining_diff = abs(difference)
                # Adjust each line in move_lines_data
                for l in move_lines_data:
                    if difference > 0 and l['debit']:
                        if l['debit'] >= remaining_diff:
                            l['debit'] -= remaining_diff
                            remaining_diff = 0
                        else:
                            remaining_diff -= l['debit']
                            l['debit'] = 0
                    elif difference < 0 and l['credit']:
                        if l['credit'] >= remaining_diff:
                            l['credit'] -= remaining_diff
                            remaining_diff = 0
                        else:
                            remaining_diff -= l['credit']
                            l['credit'] = 0
                _logger.info("Move lines adjusted line by line to balance.")
                # Delete old move lines and recreate adjusted ones
                move.line_ids.sudo().unlink()

                for vals in move_lines_data:
                    vals.update({'move_id': move.id})
                move.line_ids.sudo().create(move_lines_data)

            # Assign correct credit/debit accounts
            for line in move.line_ids.with_context(skip_account_move_synchronization=True):
                if line.credit:
                    line.account_id = credit_account
                else:
                    line.account_id = debit_account

            # Post bank payment
            bank_payment.action_post()

            # Reconcile with original payment
            to_reconcile = payment.move_id.line_ids.filtered_domain(
                [("account_id", "=", desired_account.id)]
            )
            to_reconcile |= bank_payment.move_id.line_ids.filtered_domain(
                [("account_id", "=", desired_account.id)]
            )
            to_reconcile.with_context(skip_account_move_synchronization=True).reconcile()

            # Update stages
            bank_payment._compute_x_stage_id()
            bank_payment._compute_x_next_stage_id()
            if self.move_to_next_stage:
                bank_payment.with_context(
                    do_not_call_wizard=True, entry_date=self.date
                ).action_move_to_next_stage()

            # Link original payment to bank payment
            payment.related_payment_id = bank_payment

        return res

    def _clone_payment(self, payment):
        payment_method_name = payment.payment_method_name
        payment_type = payment.payment_type
        payment_method_line_ids = (
            self.destination_journal_id.inbound_payment_method_line_ids
        )
        payment_method_line_ids |= (
            self.destination_journal_id.outbound_payment_method_line_ids
        )
        payment_method_line_id = payment_method_line_ids.filtered_domain(
            [
                ("name", "=", payment_method_name),
                ("payment_type", "=", payment_type),
            ]
        )
        if self.journal_id.x_type == "to_be_cashed" and self.payment_method_id.name == 'Effet':
            next_journal_id = self.journal_id.id
            destination_journal_id = self.destination_journal_id.id
        else:
            next_journal_id = self.destination_journal_id.id
            destination_journal_id = self.journal_id.id
        bank_payment = payment.with_context(created_from_wizard=True).copy(
            {
                "date": self.date,
                "journal_id": next_journal_id,
                "destination_journal_id": destination_journal_id,
                "payment_method_line_id": payment_method_line_id.id,
                "operation_type": self.x_banknote_type,
                "transaction_number": payment.transaction_number,
                "due_date": payment.due_date,
                "check_certified": payment.check_certified,
                "ref": payment.name,
                "payment_type": payment.payment_type,
                "partner_type": payment.partner_type,
                "related_payment_id": payment.id,
            }
        )
        return bank_payment
