from odoo import SUPERUSER_ID, api, exceptions, fields, models, _
from odoo.tools import format_date


class AccountPayment(models.Model):
    _inherit = "account.payment"

    x_stage_id = fields.Many2one(
        comodel_name="account.payment.method.stage",
        string="Étape actuelle",
        compute="_compute_x_stage_id",
        store=True,
        readonly=False,
        index=True,
        tracking=True,
        copy=False,
        group_expand="_read_group_stage_ids",
        ondelete="restrict",
        domain="[('payment_method_id', '=', payment_method_id)]",
    )
    x_next_stage_id = fields.Many2one(
        string="Étape suivante",
        comodel_name="account.payment.method.stage",
        compute="_compute_x_next_stage_id",
        store=True,
        copy=False,
    )
    x_auto_created = fields.Boolean(
        help=_("If Payment has been created automatically from the invoice/bill"),
        default=False,
        copy=False,
    )
    x_to_reconcile_line_ids = fields.Many2many(comodel_name="account.move.line")

    # check fields
    customer_bank = fields.Char(string="Banque Client")
    check_certified = fields.Boolean(
        string="Chèque Certifié", tracking=True, copy=False
    )
    confirmation_number = fields.Char(
        string="Numéro Confirmation", tracking=True, copy=False
    )

    # check, banknote fields
    customer_bank_id = fields.Many2one(
        string="Banque Client",
        comodel_name="res.partner.bank",
        readonly=True,
        states={"draft": [("readonly", False)]},
        domain="[('partner_id', '=', partner_id)]",
        compute="_compute_customer_bank_id",
        store=True,
    )
    transaction_number = fields.Char(
        string="Numéro de la valeur", tracking=True, copy=False
    )
    due_date = fields.Date(string="Date d'échéance", tracking=True, copy=False)

    # banknote fields
    operation_type = fields.Selection(
        string="Opération",
        selection=[("at_due_date", "Encaissement"), ("before_due_date", "Escompte")],
        tracking=True,
        copy=False,
    )
    # Deprecated
    operation_date = fields.Date(string="Date d'opération", tracking=True, copy=False)

    # bank transfer fields
    from_account_id = fields.Many2one(
        string="Compte expéditeur",
        comodel_name="res.partner.bank",
        tracking=True,
        copy=False,
    )
    to_account_id = fields.Many2one(
        string="Compte du destinataire",
        comodel_name="res.partner.bank",
        tracking=True,
        copy=False,
    )
    transaction_number_formatted = fields.Char(
        compute="_compute_transaction_number_formatted", store=True, index=True
    )

    hide_next_step_button = fields.Boolean(compute="_compute_hide_next_step_button")
    related_payment_id = fields.Many2one(
        string="Paiement associé", comodel_name="account.payment"
    )

    @api.depends("partner_id")
    def _compute_customer_bank_id(self):
        for payment in self:
            if (
                not payment.customer_bank_id
                or payment.customer_bank_id.partner_id != payment.partner_id
            ):
                payment.customer_bank_id = fields.first(payment.partner_id.bank_ids)

    @api.onchange("payment_method_line_id")
    def _set_account_ids(self):
        from_account_domain = []
        to_account_domain = []
        if self.payment_method_code == "v-transfer":
            partner_bank_ids = self.partner_id.bank_ids
            company_bank_ids = self.company_id.bank_ids
            if self.payment_type == "inbound":
                self.from_account_id = partner_bank_ids and partner_bank_ids[0]
                self.to_account_id = self.journal_id.bank_account_id
                from_account_domain = [("partner_id", "=", self.partner_id.id)]
                to_account_domain = [("partner_id", "=", self.company_id.partner_id.id)]
            elif self.payment_type == "outbound":
                self.from_account_id = self.journal_id.bank_account_id
                self.to_account_id = partner_bank_ids and partner_bank_ids[0]
                from_account_domain = [
                    ("partner_id", "=", self.company_id.partner_id.id)
                ]
                to_account_domain = [("partner_id", "=", self.partner_id.id)]

        else:
            self.partner_bank_id = False
            self.from_account_id = False
            self.to_account_id = False
        return {
            "domain": {
                "from_account_id": from_account_domain,
                "to_account_id": to_account_domain,
            }
        }

    @api.depends("payment_method_id", "state")
    def _compute_x_stage_id(self):
        for payment in self:
            payment_method_id = payment.payment_method_id
            if payment_method_id and payment.state == "posted":
                default_stage_id = fields.first(payment._get_available_stages())
                payment.x_stage_id = default_stage_id
                payment._check_for_reconcile_stage(default_stage_id)

    @api.depends("x_stage_id")
    def _compute_x_next_stage_id(self):
        for payment in self:
            payment.x_next_stage_id = (
                payment._get_next_stage_id() if payment.x_stage_id else False
            )

    def _compute_hide_next_step_button(self):
        available_stage_ids = self._get_available_stages().filtered_domain(
            [("type", "not in", ("butterfly", "prior_notice", "unpaid"))]
        )
        for payment in self:
            payment.hide_next_step_button = True
            if (
                available_stage_ids
                and payment._get_current_stage_id() in available_stage_ids
                and available_stage_ids[-1] != payment._get_current_stage_id()
                and payment.state == "posted"
            ):
                payment.hide_next_step_button = False

    @api.depends("partner_id", "journal_id", "transaction_number", "date")
    def _compute_transaction_number_formatted(self):
        for payment in self:
            if payment.payment_type == "inbound" and payment.payment_method_code in (
                "v-check",
                "v-banknote",
            ):
                year = (payment.date or fields.date.today).year
                bank_name = payment.customer_bank_id.bank_name
                partner_id = payment.partner_id.id or "NA"
                transaction_number = payment.transaction_number
                payment.transaction_number_formatted = (
                    f"{transaction_number}-"
                    f"{partner_id}-{bank_name}-{payment.journal_id.name}-{year}"
                )
            else:
                payment.transaction_number_formatted = None

    @api.constrains("partner_id", "journal_id", "transaction_number", "date")
    def _check_for_transaction_number(self):
        for payment in self:
            if payment.payment_type == "inbound" and payment.payment_method_code in (
                "v-check",
                "v-banknote",
            ):
                transaction_number_exists = self.search_count(
                    [
                        (
                            "transaction_number_formatted",
                            "=",
                            payment.transaction_number_formatted,
                        )
                    ]
                )
                if transaction_number_exists > 2:
                    msg = (
                        "Le numéro de la valeur doit être unique par client. "
                        + payment.transaction_number_formatted
                    )
                    raise exceptions.ValidationError(msg)

    def _get_available_stages(self):
        self.ensure_one()
        return self.payment_method_id.stage_ids

    def _get_current_stage_id(self):
        self.ensure_one()
        return self.x_stage_id

    def _get_next_stage_id(self, stage_id=None):
        """
        based on the current stage of the payment
        we get the next stage based on the sequence.
        :param stage_id: next stage after that one
        :return: stage_id record
        """
        self.ensure_one()
        # get available stage_ids
        available_stage_ids = self._get_available_stages()
        current_stage_id = stage_id or self.x_stage_id
        next_stage_ids = available_stage_ids.filtered_domain(
            [("sequence", ">", current_stage_id.sequence)]
        )
        next_stage_id = next_stage_ids and next_stage_ids[0]
        return next_stage_id

    def action_move_to_next_stage(self) -> None:
        """
        Move to the next available stage_id
        :return: None
        """
        for payment in self:
            # if the next stage_id is butterfly, prior notice or unpaid
            # the button from the form view will be hidden
            # but the user can use the action from the tree view
            if payment._get_next_stage_id().type in (
                "butterfly",
                "prior_notice",
                "unpaid",
            ):
                return
            payment._check_for_last_stage_existance()
            payment._check_for_payment_batch_stage()
            payment._check_for_payment_bank_statement()
            payment._action_move_to_next_stage()

    def _action_move_to_next_stage(self) -> None:
        next_stage_id = self._get_next_stage_id()
        self.x_stage_id = next_stage_id
        self._check_for_reconcile_stage(self.x_stage_id)

    def _check_for_reconcile_stage(self, stage_id) -> None:
        if stage_id.type == "reconcile" and self.x_auto_created:
            self.x_to_reconcile_line_ids.filtered(
                lambda line: not line.reconciled
            ).reconcile()

    def _check_for_payment_batch_stage(self) -> None:
        """
        if the next stage has a type of must_be_sent then
        we can't move to that stage until we create a payment batch
        :return: None
        """
        self.ensure_one()
        next_stage_id = self._get_next_stage_id()
        if (
            next_stage_id.type == "must_be_sent"
            and not self.batch_payment_id
            or (self.batch_payment_id and not self.is_move_sent)
        ):
            raise exceptions.ValidationError(
                "Ce paiement doit avoir un bordereau validé et envoyé"
            )

    def _check_for_payment_bank_statement(self) -> None:
        """
        if the next stage has a type of in_bank then
        we can't move to that stage until we create a bank statement
        :return: None
        """
        self.ensure_one()
        next_stage_id = self._get_next_stage_id()
        if (
            next_stage_id.type == "in_bank"
            and self.payment_type == "inbound"
            and not self.reconciled_statement_line_ids
        ):
            raise exceptions.ValidationError(
                "Ce paiement doit avoir un relevé bancaire"
            )

    def _check_for_last_stage_existance(self):
        """
        In case the user in some way clicked the next button
        when he is already in the last stage, so we raise an error
        Note: the button will be invisible is we are in the last stage
        :return:
        """
        self.ensure_one()
        next_stage_id = self._get_next_stage_id()
        if not next_stage_id:
            raise exceptions.ValidationError("Vous avez déjà atteint la dernière étape")

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        search_domain = [("id", "in", stages.ids)]

        # perform search
        stage_ids = stages._search(
            search_domain, order=order, access_rights_uid=SUPERUSER_ID
        )
        return stages.browse(stage_ids)

    @api.autovacuum
    def _check_payment_checks(self):
        domain = [
            ("payment_method_code", "=", "v-check"),
            ("check_certified", "=", True),
            ("is_reconciled", "=", False),
        ]
        # from 8 days or more if the payment is still not reconciled, yet
        # we will send a notification message to the accounting group manager
        payment_ids = self.search(domain).filtered(
            lambda payment: (fields.date.today() - payment.date).days > 7
        )
        admin_group = self.env.ref("account.group_account_manager")
        user_ids = admin_group.users
        if user_ids and payment_ids:
            channel_name = admin_group.display_name
            message = "<p>Veuillez noter que les paiements figurant sur la liste"
            message += " des chèques certifiés seront considérés comme dépassés"
            message += " après 8 jours:</p><ul>"
            for payment in payment_ids:
                message += f'<li><a href="#" data-oe-model="{self._name}" '
                message += f'data-oe-id="{payment.id}">{payment.name}</a></li>'
            message += "</ul>"
            self._base_send_a_message(user_ids, channel_name, message)

    def action_notify_about_unsent_payments(self):
        payment_ids = self.search(
            [("payment_type", "=", "inbound"), ("x_stage_id.type", "=", "must_be_sent")]
        )
        group = self.env.ref("account.group_account_readonly")
        user_ids = group.users
        if user_ids and payment_ids:
            channel_name = "Paiements"
            message = "<p>La liste des paiements doit être envoyée à la banque:"
            message += "</p><ul>"
            for payment in payment_ids:
                message += f'<li><a href="#" data-oe-model="{self._name}" '
                message += f'data-oe-id="{payment.id}">{payment.name}</a></li>'
            message += "</ul>"
            self._base_send_a_message(user_ids, channel_name, message)

    @api.depends("partner_id", "journal_id", "destination_journal_id")
    def _compute_is_internal_transfer(self):
        old_states = {}
        # we are passing the state using the context
        # so the field is not editable in the interface anymore
        # so if we set it as True
        # odoo should not reset it as False
        for payment in self:
            if payment.is_internal_transfer:
                old_states[payment] = payment.is_internal_transfer
        res = super(AccountPayment, self)._compute_is_internal_transfer()

        for payment in old_states:
            payment.is_internal_transfer = old_states[payment]

        return res

    def _get_custom_aml_default_display_name_list(self):
        self.ensure_one()
        if self.payment_method_code.startswith("v-"):
            values = []
            values.append(("label", f"{self.payment_method_name}"))
            if self.transaction_number:
                values.append(("label", f" {self.transaction_number} "))
                due_date = format_date(self.env, fields.Date.to_string(self.due_date))
                values.append(
                    (
                        "label",
                        f"{due_date}",
                    )
                )
            if self.partner_id:
                values += [
                    ("sep", " - "),
                    ("partner", self.partner_id.display_name),
                ]
            return values

    def _get_aml_default_display_name_list(self):
        """
        @Overridden
        Hook allowing custom values when constructing the
        default label to set on the journal items.

        :return: A list of terms to concatenate all together. E.g.
            [
                ('label', "Vendor Reimbursement"),
                ('sep', ' '),
                ('amount', "$ 1,555.00"),
                ('sep', ' - '),
                ('date', "05/14/2020"),
            ]
        """
        values = self._get_custom_aml_default_display_name_list()
        if not values:
            return super(AccountPayment, self)._get_aml_default_display_name_list()
        return values
