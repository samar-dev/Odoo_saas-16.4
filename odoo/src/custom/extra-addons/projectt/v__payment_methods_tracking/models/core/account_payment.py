from markupsafe import Markup
from odoo import SUPERUSER_ID, api, exceptions, fields, models
from odoo.exceptions import UserError
from odoo.tests.common import Form


class AccountPayment(models.Model):
    _inherit = "account.payment"

    # differentiate between the old stages and the new one
    # for UX when the customer uses filters
    x_stage_id = fields.Many2one(string="Étape actuelle (old)")
    x_next_stage_id = fields.Many2one(string="Étape suivante (old)")
    x_old_account_id = fields.Many2one(string="old commission")
    x_new_stage_id = fields.Many2one(
        comodel_name="payment.method.line.stage.line",
        string="Étape actuelle",
        compute="_compute_x_stage_id",
        store=True,
        readonly=False,
        index=True,
        tracking=True,
        copy=False,
        group_expand="_read_group_new_stage_ids",
        ondelete="restrict",
        domain="[('payment_method_line_id', '=', payment_method_line_id),"
        " ('banknote_type', 'in', (operation_type, False))]",
    )
    x_new_next_stage_id = fields.Many2one(
        string="Étape suivante",
        comodel_name="payment.method.line.stage.line",
        compute="_compute_x_next_stage_id",
        store=True,
        copy=False,
    )
    # we use another payment_id as an inverse_anme instead of the original payment_id
    # because using the old one will cause an issue for us when we post the move
    x_move_ids = fields.One2many(
        comodel_name="account.move", inverse_name="x_payment_id"
    )
    certificate_name = fields.Char()
    certificate_file = fields.Binary(string="Attestation", readonly=True)
    button_regularize_hidden = fields.Boolean(
        compute="_compute_button_regularize_hidden"
    )
    is_verified = fields.Boolean(
        string="Vérifié",
        default=lambda self: not self.env.company.x_verify_payment,
        tracking=True,
    )
    show_is_verified = fields.Boolean(compute="_compute_show_is_verified")

    def action_initiate_stages(self):
        """
        Will be called from an action server temporarily
        Used to set the new stage of the payment based on the old one
        :return: None
        """
        for payment_id in self:
            if payment_id.state == "posted":
                available_stages = payment_id._get_available_stages()
                if not payment_id.x_new_stage_id:
                    new_stage = available_stages.filtered(
                        lambda stage: stage.name == payment_id.x_stage_id.name
                        and payment_id.operation_type == stage.banknote_type
                    ) or fields.first(available_stages)
                    payment_id.with_context(tracking_disable=True).x_new_stage_id = (
                        new_stage
                    )

    @api.depends("company_id")
    def _compute_show_is_verified(self):
        for payment in self:
            payment.show_is_verified = self.env.company.x_verify_payment

    def action_toggle_is_verified(self):
        self.ensure_one()
        self.is_verified = not self.is_verified

    @api.depends("payment_method_line_id", "state")
    def _compute_x_stage_id(self):
        # Overridden
        for payment in self:
            payment_method_line_id = payment.payment_method_line_id
            if payment_method_line_id and payment.state == "posted":
                available_stages = payment._get_available_stages()
                default_stage_id = fields.first(available_stages)
                payment.x_new_stage_id = default_stage_id
                payment._check_for_reconcile_stage(default_stage_id)

    @api.depends("x_new_stage_id")
    def _compute_x_next_stage_id(self):
        # Overridden
        for payment in self:
            payment.x_new_next_stage_id = payment._get_next_stage_id()

    def _compute_button_regularize_hidden(self):
        for payment in self:
            payment.button_regularize_hidden = not (
                payment.state == "posted"
                and payment.is_unpaid == "yes"
                and not payment.replacement_payment_count
                and payment.payment_method_code in ("v-check", "v-banknote")
                and payment.payment_type == "inbound"
            )

    def _compute_replace_button_hidden(self):
        """
        @Overridden
        Replace button will only be visible
        if the payment is unpaid or butterfly and not fully replaced and must be posted
        the difference between the original and this one is the state of the payment
        :return: None
        """
        for payment in self:
            payment.replace_button_hidden = not (
                payment.state == "posted"
                and (payment.is_unpaid == "yes" or payment.is_butterfly == "yes")
                and not payment.is_replaced
            )

    def _get_available_stages(self):
        # Overridden
        self.ensure_one()
        stage_id = self.payment_method_line_id.payment_method_line_stage_id
        available_new_stage_ids = stage_id.payment_method_line_stage_line_ids
        return available_new_stage_ids

    def _get_current_stage_id(self):
        # Overridden
        self.ensure_one()
        return self.x_new_stage_id

    def _get_next_stage_id(self, stage_id=None):
        """
        @Overridden
        based on the current stage of the payment
        we get the next stage based on the sequence.
        :param stage_id: next stage after that one
        :return: stage_id record
        """
        self.ensure_one()
        # get available stage_ids
        available_stage_ids = self._get_available_stages()
        current_stage_id = stage_id or self.x_new_stage_id
        next_stage_id = fields.first(
            available_stage_ids.filtered_domain(
                [
                    ("sequence", ">", current_stage_id.sequence),
                    ("banknote_type", "in", (self.operation_type, False)),
                ]
            )
        )
        return next_stage_id

    @api.model
    def _read_group_new_stage_ids(self, stages, domain, order):
        search_domain = [("id", "in", stages.ids)]

        # perform search
        stage_ids = stages._search(
            search_domain, order=order, access_rights_uid=SUPERUSER_ID
        )
        return stages.browse(stage_ids)

    def _action_move_to_next_stage(self) -> None:
        # Overridden
        self.ensure_one()
        next_stage_id = self._get_next_stage_id()
        self.x_new_stage_id = next_stage_id
        self._check_for_reconcile_stage(self.x_new_stage_id)

    def button_open_journal_entry(self):
        # Overridden
        replacement_payment_ids = self.replacement_payment_ids
        replacement_reconciled_statements = (
            replacement_payment_ids.reconciled_statement_line_ids
        )
        move_line_ids = (
            self.move_id.line_ids.ids
            + self.x_move_ids.line_ids.ids
            + self.reconciled_statement_line_ids.line_ids.move_id.line_ids.ids
            + replacement_payment_ids.move_id.line_ids.ids
            + replacement_payment_ids.x_move_ids.line_ids.ids
            + replacement_reconciled_statements.line_ids.move_id.line_ids.ids
        )
        action = {
            "name": self.name,
            "view_mode": "tree,form",
            "res_model": "account.move.line",
            "type": "ir.actions.act_window",
            "context": {
                "create": 0,
                "edit": 0,
            },
            "target": "self",
            "domain": [
                (
                    "id",
                    "in",
                    move_line_ids,
                )
            ],
        }
        return action

    def action_set_butterfly(self):
        # Overridden
        self.ensure_one()
        if not self._context.get("do_not_call_wizard"):
            return self._call_next_stage_payment_wiz(callback="action_set_butterfly")
        available_stages = self._get_available_stages()
        butterfly = available_stages.filtered_domain([("type", "=", "butterfly")])
        in_bank = available_stages.filtered_domain([("type", "=", "in_bank")])
        debit_account = butterfly.account_id
        credit_account = in_bank.account_id
        # swap in case the payment is outbound
        # the credit become the debit and vice versa
        if self.payment_type == "outbound":
            credit_account, debit_account = debit_account, credit_account
        self._create_journal_entry(
            credit_account=credit_account, debit_account=debit_account
        )
        self.write({"x_new_stage_id": butterfly.id, "is_butterfly": "yes"})

    def action_set_prior_notice(self):
        # Overridden
        self.ensure_one()
        if not self._context.get("do_not_call_wizard"):
            return self._call_next_stage_payment_wiz(callback="action_set_prior_notice")
        available_stages = self._get_available_stages()
        prior_notice = available_stages.filtered_domain([("type", "=", "prior_notice")])
        in_bank = available_stages.filtered_domain([("type", "=", "in_bank")])
        debit_account = prior_notice.account_id
        credit_account = in_bank.account_id
        # swap in case the payment is outbound
        # the credit become the debit and vice versa
        if self.payment_type == "outbound":
            credit_account, debit_account = debit_account, credit_account
        self._create_journal_entry(
            credit_account=credit_account, debit_account=debit_account
        )
        self.write({"x_new_stage_id": prior_notice.id, "is_prior_notice": "yes"})
        message = f"Blocage suite préavis {self.name}"
        if self.transaction_number:
            message += (
                f" - {self.payment_method_name} "
                f"{self.transaction_number} {self.due_date}"
            )
        self._set_customer_blocked_state(message=message, state="blocked")

    def action_set_paid(self):
        # Overridden
        self.ensure_one()
        available_stage_ids = self._get_available_stages()
        in_bank = available_stage_ids.filtered_domain([("type", "=", "in_bank")])
        write_vals = {"x_new_stage_id": in_bank.id, "is_paid": True}
        if self.is_prior_notice == "yes" or self.is_butterfly == "yes":
            if not self._context.get("do_not_call_wizard"):
                return self._call_next_stage_payment_wiz(callback="action_set_paid")
            current_stage = self._get_current_stage_id()
            credit_account = current_stage.account_id
            debit_account = in_bank.account_id

            # swap in case the payment is outbound
            # the credit become the debit and vice versa
            if self.payment_type == "outbound":
                credit_account, debit_account = debit_account, credit_account
            self._create_journal_entry(
                credit_account=credit_account, debit_account=debit_account
            )
            if self.is_prior_notice == "yes":
                write_vals["is_prior_notice"] = "fixed"
                # check if the customer still have unpaid payments
                # or prior_notice payments
                payment_domain = [
                    ("partner_id", "=", self.partner_id.id),
                    ("payment_type", "=", "inbound"),
                    ("partner_type", "=", "customer"),
                    ("company_id", "=", self.env.company.id),
                    ("state", "=", "posted"),
                    "|",
                    ("is_prior_notice", "=", "yes"),
                    ("is_unpaid", "=", "yes"),
                ]
                payments_to_fix = self.search(payment_domain)
                if not payments_to_fix:
                    message = f"Déblocage suite régularisation préavis {self.name}"
                    if self.transaction_number:
                        message += (
                            f" - {self.payment_method_name} "
                            f"{self.transaction_number} {self.due_date}"
                        )
                    self._set_customer_blocked_state(message=message, state="unblocked")
            elif self.is_butterfly == "yes":
                write_vals["is_butterfly"] = "fixed"
        self.write(write_vals)

    def action_set_all_paid(self):
        # Get all the records from active_ids
        active_ids = self.env.context.get("active_ids", [])

        if not active_ids:
            raise exceptions.ValidationError("No active records found to process.")

        # Browse the records once
        records = self.browse(active_ids)

        # Filter the records where 'is_paid' is True
        check_paid = records.filtered(lambda ml: ml.is_paid)
        if check_paid:
            raise exceptions.ValidationError(
                "Vous ne pouvez pas payer, un paiement deja paye."
            )

        # Loop through all active_ids and process each record individually
        for record in records:
            # Ensure we're working with a single record
            record.ensure_one()

            # Get available stages and filter for 'in_bank'
            available_stage_ids = record._get_available_stages()
            in_bank = available_stage_ids.filtered_domain([("type", "=", "in_bank")])

            # Prepare the write values
            write_vals = {"x_new_stage_id": in_bank.id, "is_paid": True}

            # Handle specific conditions for 'prior_notice' or 'butterfly'
            if record.is_prior_notice == "yes" or record.is_butterfly == "yes":
                if not record._context.get("do_not_call_wizard"):
                    return record._call_next_stage_payment_wiz(
                        callback="action_set_paid"
                    )

                current_stage = record._get_current_stage_id()
                credit_account = current_stage.account_id
                debit_account = in_bank.account_id

                # Swap in case the payment is outbound (credit becomes debit and vice versa)
                if record.payment_type == "outbound":
                    credit_account, debit_account = debit_account, credit_account

                # Create the journal entry for the payment
                record._create_journal_entry(
                    credit_account=credit_account, debit_account=debit_account
                )

                if record.is_prior_notice == "yes":
                    write_vals["is_prior_notice"] = "fixed"

                    # Check if the customer still has unpaid payments or prior notice payments
                    payment_domain = [
                        ("partner_id", "=", record.partner_id.id),
                        ("payment_type", "=", "inbound"),
                        ("partner_type", "=", "customer"),
                        ("company_id", "=", record.env.company.id),
                        ("state", "=", "posted"),
                        "|",
                        ("is_prior_notice", "=", "yes"),
                        ("is_unpaid", "=", "yes"),
                    ]
                    payments_to_fix = record.search(payment_domain)
                    if not payments_to_fix:
                        message = (
                            f"Déblocage suite régularisation préavis {record.name}"
                        )
                        if record.transaction_number:
                            message += f" - {record.payment_method_name} {record.transaction_number} {record.due_date}"
                        record._set_customer_blocked_state(
                            message=message, state="unblocked"
                        )
                elif record.is_butterfly == "yes":
                    write_vals["is_butterfly"] = "fixed"

            # Update the record with the calculated values
            record.write(write_vals)

    def action_set_unpaid(self):
        self.ensure_one()
        if not self._context.get("do_not_call_wizard"):
            return self._call_next_stage_payment_wiz(callback="action_set_unpaid")
        available_stages = self._get_available_stages()
        prior_notice = available_stages.filtered_domain([("type", "=", "prior_notice")])
        in_bank = available_stages.filtered_domain([("type", "=", "in_bank")])
        unpaid = available_stages.filtered_domain([("type", "=", "unpaid")])
        credit_account_one = prior_notice.account_id
        debit_account_one = in_bank.account_id
        credit_account_two = in_bank.account_id
        debit_account_two = unpaid.account_id

        # swap in case the payment is outbound
        # the credit become the debit and vice versa
        if self.payment_type == "outbound":
            credit_account_one, debit_account_one = (
                debit_account_one,
                credit_account_one,
            )
            credit_account_two, debit_account_two = (
                debit_account_two,
                credit_account_two,
            )

        # if the payment method does not have a prior notice
        # no need to return the money to the bank account as a cancellation
        if prior_notice and credit_account_one:
            self._create_journal_entry(
                credit_account=credit_account_one, debit_account=debit_account_one
            )
        self._create_journal_entry(
            credit_account=credit_account_two, debit_account=debit_account_two
        )
        self.write({"x_new_stage_id": unpaid.id, "is_unpaid": "yes"})
        message = f"Blocage suite impayé {self.name}"
        if self.transaction_number:
            message += (
                f" - {self.payment_method_name} "
                f"{self.transaction_number} {self.due_date}"
            )
        self._set_customer_blocked_state(message=message, state="blocked")

    @api.depends(
        "move_id.line_ids.matched_debit_ids", "move_id.line_ids.matched_credit_ids"
    )
    def _compute_stat_buttons_from_reconciliation(self):
        res = super(AccountPayment, self)._compute_stat_buttons_from_reconciliation()
        for payment in self:
            # if we already got a statment attched with the payment
            # no need to use our hack to attach the statement
            # in another word the statement is being attached with the main move_id
            if not payment.reconciled_statement_lines_count:
                matching_numbers = payment.x_move_ids.line_ids.filtered(
                    lambda line: line.matching_number
                ).mapped("matching_number")
                if not matching_numbers:
                    matching_numbers = payment.move_id.line_ids.filtered(
                        lambda line: line.matching_number
                    ).mapped("matching_number")
                line_ids = self.env["account.move.line"].search(
                    [
                        ("matching_number", "in", matching_numbers),
                        ("statement_line_id", "!=", False),
                    ]
                )
                statement_line_ids = line_ids.mapped("statement_line_id")
                payment.reconciled_statement_lines_count = len(statement_line_ids)
                payment.reconciled_statement_line_ids = statement_line_ids

        return res

    def _call_next_stage_payment_wiz(self, callback):
        action = {
            "name": "Paiements",
            "view_mode": "form",
            "res_model": "next.stage.payment.wiz",
            "type": "ir.actions.act_window",
            "target": "new",
            "context": {"active_ids": self.ids, "callback": callback},
        }
        return action

    def _check_for_payment_bank_statement(self) -> None:
        """
        @Overridden
        if the next stage has a type of in_bank and the with_bank_statement is True
        then we can't move to that stage until we create a bank statement
        :return: None
        """
        self.ensure_one()
        next_stage_id = self._get_next_stage_id()
        if (
            next_stage_id.type == "in_bank"
            and next_stage_id.with_bank_statement
            and not self.reconciled_statement_line_ids
        ):
            raise exceptions.ValidationError(
                "Ce paiement doit avoir un relevé bancaire"
            )

    def _check_for_payment_verification(self):
        if self.env.company.x_verify_payment:
            for payment in self:
                if not payment.is_verified:
                    raise exceptions.ValidationError(
                        "Merci de valider le paiement avant de poursuivre"
                    )

    def action_move_to_next_stage(self):
        """
        @Overridden
        original method defined in v__payment_methods module
        each time we move from stage to another we create a journal entry
        :return: None or dict
        """

        self._check_for_payment_verification()

        if not self._context.get("do_not_call_wizard"):
            return self._call_next_stage_payment_wiz(
                callback="action_move_to_next_stage"
            )
        for payment in self:
            # if the next stage_id is butterfly,  prior notice or unpaid
            # the button from the form view will be hidden
            # but the user can use the action from the tree view
            if payment._get_next_stage_id().type in (
                "butterfly",
                "prior_notice",
                "unpaid",
            ):
                return
            if payment.original_payment_ids:
                payment = payment.with_context(skip_account_move_synchronization=True)
            payment._check_for_last_stage_existance()
            payment._check_for_payment_batch_stage()
            payment._check_for_payment_bank_statement()
            # next_stage will be empty in case we are already in the last stage
            # and if it is empty it means we have no account_id
            current_stage = payment.x_new_stage_id
            next_stage = payment._get_next_stage_id()
            credit_account = current_stage.account_id
            debit_account = next_stage.account_id

            without_journal_entry = (
                self._context.get("do_not_create_journal_entry")
                or not current_stage.with_journal_entry
            )

            # no need to create a journal entry
            # because it will be created using the bank statement
            if next_stage.type == "in_bank" and next_stage.with_bank_statement:
                payment.with_context(
                    do_not_create_journal_entry=without_journal_entry
                )._action_move_to_next_stage()
            else:
                payment.with_context(
                    do_not_create_journal_entry=without_journal_entry
                )._pre_create_journal_entry(
                    credit_account, current_stage, debit_account, next_stage
                )

    def _pre_create_journal_entry(
        self, credit_account, current_stage, debit_account, next_stage
    ) -> None:
        """
        Prepare the necessary accounts to create the journal entry
        after creating the journal entry we simply move the payment to the next stage
        :param credit_account: account to use when creating the credit line.
        :param current_stage: used for exceptions to show
        which stage is missing an account.
        :param debit_account: account to use when creating the debit line.
        :param next_stage: used for exceptions to show
        which stage is missing an account.
        :return: None
        """
        self.ensure_one()
        if credit_account and debit_account:
            # if payment is for supplier we inverse the accounts
            # because the credit account in inbound
            # will become debit account in outbound
            if self.payment_type == "outbound" and self.partner_type == "supplier":
                credit_account, debit_account = debit_account, credit_account
            self._create_journal_entry(credit_account, debit_account)
        # we are not in the last stage
        # but there are no accounts defined
        # either for both stages or for one of them
        elif current_stage.with_journal_entry and current_stage and next_stage:
            messages = []
            prefix = "Le compte pour l'étape suivante"
            if not credit_account:
                messages.append(f"{prefix} {current_stage.name} n'est pas défini.")
            if not debit_account:
                messages.append(f"{prefix} {next_stage.name} n'est pas défini.")
            message = "\n".join(messages)
            raise exceptions.ValidationError(message)
        self._action_move_to_next_stage()

    def _create_journal_entry(
        self, credit_account, debit_account, amount=0, label=None
    ):
        if self._context.get("do_not_create_journal_entry"):
            return
        self.ensure_one()
        with Form(self.with_context(move_type="entry").env["account.move"]) as move:
            move.ref = self.name
            move.date = self._context.get("entry_date") or fields.Date.today()
            default_line_name = "".join(
                x[1] for x in self._get_aml_default_display_name_list()
            )
            with move.line_ids.new() as line:
                line.name = label or default_line_name
                line.account_id = (
                    debit_account if self.payment_type == "inbound" else credit_account
                )
                line.partner_id = self.partner_id
                line.debit = (
                    (amount or self.amount) if self.payment_type == "inbound" else 0
                )
                line.credit = (
                    (amount or self.amount) if self.payment_type == "outbound" else 0
                )
            with move.line_ids.new() as line:
                line.name = label or default_line_name
                line.account_id = (
                    credit_account if self.payment_type == "inbound" else debit_account
                )
                line.partner_id = self.partner_id
                line.debit = (
                    (amount or self.amount) if self.payment_type == "outbound" else 0
                )
                line.credit = (
                    (amount or self.amount) if self.payment_type == "inbound" else 0
                )
        move_id = move.save()

        if self.destination_journal_id and self.payment_method_line_id.name == "Effet":
            destination_journal_id = self.destination_journal_id
        else:
            destination_journal_id = self.journal_id

        move_id.journal_id = destination_journal_id
        move_id.action_post()
        # try to reconcile before adding the new move to the existing x_move_ids
        self._reconcile_move_lines(move_id)
        self.x_move_ids |= move_id
        msg = (
            "Une écriture comptable a été créée"
            f": <a href=# data-oe-model=account.move"
            f" data-oe-id={move_id.id}>{move_id.name}</a>"
        )
        self.message_post(body=Markup(msg))

    def _reconcile_move_lines(self, new_move_id):
        self.ensure_one()
        # get only the lines that we can reconcile
        if self.payment_type == "inbound" and self.partner_type == "customer":
            self._reconcile_inbound_based(new_move_id)
        elif self.payment_type == "outbound" and self.partner_type == "supplier":
            self._reconcile_outbound_based(new_move_id)

    def _reconcile_inbound_based(self, new_move_id):
        credit_line = new_move_id.line_ids.filtered(
            lambda line: line.account_id.reconcile and line.credit > 0
        )
        # check first if we can match with the initial move_id of the payment
        if credit_line:
            # check against the initial move_id of the payment
            debit_line = self.move_id.line_ids.filtered(
                lambda line: line.account_id.reconcile
                and not line.reconciled
                and line.debit == credit_line.credit
                and line.account_id == credit_line.account_id
            )

            # check against the existing x_move_ids
            if not debit_line:
                debit_line = self.x_move_ids.line_ids.filtered(
                    lambda line: line.account_id.reconcile
                    and not line.reconciled
                    and line.debit == credit_line.credit
                    and line.account_id == credit_line.account_id
                )

            if debit_line:
                (debit_line + credit_line).reconcile()

    def _reconcile_outbound_based(self, new_move_id):
        debit_line = new_move_id.line_ids.filtered(
            lambda line: line.account_id.reconcile and line.debit > 0
        )
        # check first if we can match with the initial move_id of the payment
        if debit_line:
            # check against the initial move_id of the payment
            credit_line = self.move_id.line_ids.filtered(
                lambda line: line.account_id.reconcile
                and not line.reconciled
                and line.credit == debit_line.debit
                and line.account_id == debit_line.account_id
            )

            # check against the existing x_move_ids
            if not credit_line:
                credit_line = self.x_move_ids.line_ids.filtered(
                    lambda line: line.account_id.reconcile
                    and not line.reconciled
                    and line.credit == debit_line.debit
                    and line.account_id == debit_line.account_id
                )

            if credit_line:
                (credit_line + debit_line).reconcile()

    def action_regularize_payment(self):
        self.ensure_one()
        action = {
            "name": self.name,
            "view_mode": "form",
            "res_model": "regularize.by.certificate.wiz",
            "type": "ir.actions.act_window",
            "target": "new",
        }
        return action

    def change_change_effet(self):
        for record in self:
            # Track whether we need to change operation_type
            new_operation_type = None
            # Iterate over the items in the line_ids
            for item in record.line_ids:
                if (
                    item.account_id.code == "531400"
                    and record.operation_type == "before_due_date"
                ):
                    # Find account with code 531300
                    account_531300 = self.env["account.account"].search(
                        [("code", "=", "531300")], limit=1
                    )
                    if account_531300:
                        item.write(
                            {"account_id": account_531300.id}
                        )  # Update both code and account_id
                    new_operation_type = "at_due_date"
                    self.x_old_account_id = self.x_new_stage_id.account_commission_id.id
                    self.x_new_stage_id.account_commission_id = False
                    self.x_new_stage_id.banknote_type = "at_due_date"
                elif (
                    item.account_id.code == "531300"
                    and record.operation_type == "at_due_date"
                ):
                    # Find account with code 531400
                    account_531400 = self.env["account.account"].search(
                        [("code", "=", "531400")], limit=1
                    )
                    if account_531400:
                        item.write(
                            {"account_id": account_531400.id}
                        )  # Update both code and account_id
                    new_operation_type = "before_due_date"

            # After checking all line_items, update the operation_type if needed
            if new_operation_type:
                record.write({"operation_type": new_operation_type})
                record.write({"show_commission_page": True})

    def action_replace_payment(self):
        # Overridden
        to_replace_payments = self.filtered_domain(
            ["|", ("is_unpaid", "=", "yes"), ("is_butterfly", "=", "yes")]
        )
        if len(set(to_replace_payments.mapped("partner_type"))) > 1:
            raise exceptions.ValidationError("Les paiements doivent être du même type")
        if len(set(to_replace_payments.mapped("partner_id"))) > 1:
            raise exceptions.ValidationError(
                "Les paiements doivent partager le même partenaire"
            )
        if not to_replace_payments:
            return
        original_amount = sum(to_replace_payments.mapped("amount"))
        replaced_amount = sum(to_replace_payments.mapped("replaced_amount"))
        action = {
            "name": "Paiement",
            "view_mode": "form",
            "res_model": "account.payment",
            "type": "ir.actions.act_window",
            "view_id": self.env.ref(
                "v__payment_methods.view_account_payment_form_without_header"
            ).id,
            "context": {
                "default_partner_id": self.partner_id.id,
                "default_amount": abs(original_amount - replaced_amount),
                "default_payment_type": fields.first(self).payment_type,
                "default_partner_type": fields.first(self).partner_type,
                "default_move_journal_types": ("bank", "cash"),
                "default_ref": ",".join(self.mapped("name")),
                "to_replace_payments": to_replace_payments.ids,
                "hide_factoring_button": True,
                "hide_replace_button": False,
            },
            "target": "new",
        }
        return action

    def action_add_replacement(self):
        self.ensure_one()
        # as long as we are not using an account receivable/payable for this payment,
        # so odoo will complain by passing this key in the context
        # odoo will be nice with us :)
        self = self.with_context(skip_account_move_synchronization=True)
        to_replace_payments = self._context.get("to_replace_payments")
        original_payments = (
            self.env["account.payment"]
            .browse(to_replace_payments)
            .sorted(lambda pay: (pay.amount, pay.id))
        )

        if self.payment_type == "inbound":
            self._action_add_replacement(
                amount_key="credit", original_payments=original_payments
            )
        else:
            self._action_add_replacement(
                amount_key="debit", original_payments=original_payments
            )

        for original_payment in original_payments:
            # check if the customer still have unpaid payments
            # or prior_notice payments
            payment_domain = [
                ("partner_id", "=", original_payment.partner_id.id),
                ("payment_type", "=", "inbound"),
                ("partner_type", "=", "customer"),
                ("company_id", "=", self.env.company.id),
                ("state", "=", "posted"),
                "|",
                ("is_prior_notice", "=", "yes"),
                ("is_unpaid", "=", "yes"),
            ]
            payments_to_fix = self.search(payment_domain)
            if not payments_to_fix:
                message = (
                    f"Déblocage suite régularisation impayé {original_payment.name}"
                )
                if original_payment.transaction_number:
                    message += (
                        f" - {original_payment.payment_method_name} "
                        f"{original_payment.transaction_number} "
                        f"{original_payment.due_date}"
                    )
                self._set_customer_blocked_state(message=message, state="unblocked")

    def _action_add_replacement(
        self, amount_key: str, original_payments: models.Model
    ) -> None:
        """
        replacement for inbound or outbound will be the same
        the only difference is the credit lines and debit lines
        :param amount_key: either credit or debit
        :param original_payments: the original payments being replaced
        :return: None
        """
        self.ensure_one()
        assert amount_key in ("credit", "debit")
        opposite_key = "credit" if amount_key == "debit" else "debit"
        replacement_amount = self.amount
        # it depends on amount_key it will be either credit line or debit line
        first_line = self.move_id.line_ids.filtered(
            lambda line: line.account_id.reconcile
            and not line.reconciled
            and line[amount_key] > 0
        )
        second_line = self.env["account.move.line"]
        # key will be the account, and the value will be a list of the amounts
        # we use it later in case we have multiple accounts.
        # so we can split the credit/debit lines in the move_id of the payment
        lines_dict = {}
        for original_payment_id in original_payments:
            # no need to add it to the original payment as a replacement
            if replacement_amount == 0:
                continue
            current_stage = original_payment_id._get_current_stage_id()
            current_account = current_stage.account_id
            amount_due = (
                original_payment_id.amount - original_payment_id.replaced_amount
            )

            if replacement_amount >= amount_due:
                replacement_amount -= amount_due
                original_payment_id.replaced_amount += amount_due
                lines_dict.setdefault(current_account, []).append(amount_due)
            else:
                original_payment_id.replaced_amount += replacement_amount
                lines_dict.setdefault(current_account, []).append(replacement_amount)
                replacement_amount = 0

            # in we have two payments being replaced,
            # and the amount being replaced is 500
            # 1. check with 500
            # 2. banknote with 500
            # only one of them will be reconciled, as long as we have a condition above
            # to skip to the next payment
            second_line |= original_payment_id.x_move_ids.line_ids.filtered(
                lambda line: line.account_id.reconcile
                and not line.reconciled
                and line[opposite_key] > 0
                and line.account_id == current_account
            )

            self.original_payment_ids |= original_payment_id
            original_payment_id.replacement_payment_ids |= self

            if original_payment_id.replaced_amount >= original_payment_id.amount:
                original_payment_id._set_payment_state(
                    write_vals={"is_replaced": True, "is_paid": True}, state="yes"
                )

        # in case we replace multiple payment with multiple payment methods
        # we will modify the credit/debit line amount add a new credit/debit lines
        if len(lines_dict) > 1:
            line_index = list(self.move_id.line_ids).index(first_line)
            with Form(self.move_id) as move:
                old_label_name = first_line.name
                move.line_ids.remove(line_index)
                for account_id, amounts in lines_dict.items():
                    with move.line_ids.new() as line_o2m:
                        line_o2m.name = old_label_name
                        line_o2m.partner_id = self.partner_id
                        line_o2m.account_id = account_id
                        # O2MForm is not subscriptable,
                        # and using if else will add more complexity to CC score
                        line_o2m.credit = amount_key == "credit" and sum(amounts) or 0
                        line_o2m.debit = amount_key == "debit" and sum(amounts) or 0
            first_line = self.move_id.line_ids.filtered(
                lambda line: line.account_id.reconcile
                and not line.reconciled
                and line[amount_key] > 0
            )
        else:
            first_line.account_id = current_account

        self.action_post()

        for line_id in first_line:
            temp_line = second_line.filtered(
                lambda line: line.account_id.reconcile
                and not line.reconciled
                and line[opposite_key] > 0
                and line.account_id == line_id.account_id
            )
            if line_id and temp_line:
                (line_id + temp_line).reconcile()

    def action_draft(self):
        message = "Vous n'êtes pas autorisé à réinitialiser le paiement à ce stade"
        for payment in self:
            available_stages = payment._get_available_stages()
            current_stage = payment._get_current_stage_id()
            # the cases we allow the user to set the payment to draft
            # 1. if the payment method is not one of our custom payment methods
            # which means it doesn't have stages at all
            # 2. the payment method is one of our custom payment methods
            # and the payment is still in the first stage,
            # so after moving to the next stage
            # we prevent the user from setting the payment to draft
            if current_stage == fields.first(available_stages):
                return super(AccountPayment, self).action_draft()
            raise UserError(message)
