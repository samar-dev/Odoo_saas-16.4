from odoo import api, exceptions, fields, models

common_selection = [("yes", "Oui"), ("no", "Non"), ("fixed", "Régularisé")]


class AccountPayment(models.Model):
    _inherit = "account.payment"
    is_butterfly = fields.Selection(
        selection=common_selection,
        string="Papillon",
        default="no",
        copy=False,
        tracking=True,
    )
    is_prior_notice = fields.Selection(
        selection=common_selection,
        string="Préavis",
        default="no",
        copy=False,
        tracking=True,
    )
    is_paid = fields.Boolean(string="Cloturé", default=True, copy=False, tracking=True)
    is_unpaid = fields.Selection(
        selection=common_selection,
        string="Impayé",
        default="no",
        copy=False,
        tracking=True,
    )
    is_replaced = fields.Boolean(
        string="Remplacé", default=False, copy=False, tracking=True
    )
    butterfly_button_hidden = fields.Boolean(compute="_compute_butterfly_button_hidden")
    prior_notice_button_hidden = fields.Boolean(
        compute="_compute_prior_notice_button_hidden"
    )
    paid_button_hidden = fields.Boolean(compute="_compute_paid_button_hidden")
    unpaid_button_hidden = fields.Boolean(compute="_compute_unpaid_button_hidden")
    replace_button_hidden = fields.Boolean(compute="_compute_replace_button_hidden")
    original_payment_ids = fields.Many2many(
        string="Paiements originaux",
        comodel_name="account.payment",
        readonly=True,
        relation="account_payment_original_payments_rel",
        column1="payment_id",
        column2="original_payment_id",
    )
    original_payments_hidden = fields.Boolean(
        compute="_compute_original_payments_hidden"
    )
    replacement_payment_ids = fields.Many2many(
        comodel_name="account.payment",
        relation="account_payment_replacement_payment_rel",
        column1="payment_id",
        column2="replacement_payment_id",
    )
    replacement_payment_count = fields.Integer(
        compute="_compute_replacement_payment_count"
    )
    replaced_amount = fields.Monetary(string="Montant Remplacé")

    @api.depends("original_payment_ids")
    def _compute_original_payments_hidden(self):
        for payment in self:
            payment.original_payments_hidden = not payment.original_payment_ids

    def _compute_replacement_payment_count(self):
        for payment in self:
            payment.replacement_payment_count = len(payment.replacement_payment_ids)

    def _compute_butterfly_button_hidden(self):
        """
        Butterfly button will only be visible if we are in the desired x_stage_id
        :return: None
        """
        for payment in self:
            current_stage = payment._get_current_stage_id()
            payment.butterfly_button_hidden = not (
                current_stage.type in ("in_bank",)
                and payment.state == "posted"
                and payment.is_paid is False
                and payment._get_available_stages().filtered_domain(
                    [("type", "=", "butterfly")]
                )
            )

    def _compute_prior_notice_button_hidden(self):
        """
        Prior-notice button will only be visible if we are in the desired x_stage_id
        :return: None
        """
        for payment in self:
            current_stage = payment._get_current_stage_id()
            payment.prior_notice_button_hidden = not (
                current_stage.type in ("in_bank",)
                and payment.state == "posted"
                and payment.is_paid is False
                and payment._get_available_stages().filtered_domain(
                    [("type", "=", "prior_notice")]
                )
            )

    def _compute_paid_button_hidden(self):
        """
        Paid button will only be visible if we are in the desired x_stage_id
        :return: None
        """
        for payment in self:
            current_stage = payment._get_current_stage_id()
            payment.paid_button_hidden = not (
                current_stage.type in ("in_bank", "butterfly", "prior_notice")
                and payment.state == "posted"
                and payment.is_paid is False
            )

    def _compute_unpaid_button_hidden(self):
        """
        Unpaid button will only be visible if we are in the desired x_stage_id
        :return: None
        """
        for payment in self:
            current_stage = payment._get_current_stage_id()
            available_stages = payment._get_available_stages()
            # if we have a prior_notice stage,
            # then the button should appear when we reach the prior_notice
            # otherwise the button should appear at in_bank stage
            # of course we should have an unpaid stage as a requirement
            current_stage_type = "in_bank"
            if "prior_notice" in available_stages.mapped("type"):
                current_stage_type = "prior_notice"
            payment.unpaid_button_hidden = not (
                current_stage.type == current_stage_type
                and payment.state == "posted"
                and available_stages.filtered_domain([("type", "=", "unpaid")])
                and not payment.is_paid
            )

    def _compute_replace_button_hidden(self):
        """
        Replace button will only be visible
        if the payment is unpaid or butterfly and the state is cancelled
        and the total amount of the replacement payments less than the original one
        :return: None
        """
        for payment in self:
            payment.replace_button_hidden = not (
                payment.state == "cancel"
                and (payment.is_unpaid == "yes" or payment.is_butterfly == "yes")
                and not payment.is_replaced
            )

    def action_set_butterfly(self):
        self.ensure_one()
        available_stage_ids = self.payment_method_id.stage_ids
        butterfly_stage = available_stage_ids.filtered_domain(
            [("type", "=", "butterfly")]
        )
        self.write({"x_stage_id": butterfly_stage.id, "is_butterfly": "yes"})

    def action_set_prior_notice(self):
        self.ensure_one()
        available_stage_ids = self.payment_method_id.stage_ids
        prior_notice_stage = available_stage_ids.filtered_domain(
            [("type", "=", "prior_notice")]
        )
        if prior_notice_stage:
            self.x_stage_id = prior_notice_stage
        self.is_prior_notice = "yes"
        message = f"Blocage suite préavis {self.name}"
        if self.transaction_number:
            message += (
                f" {self.payment_method_name} {self.transaction_number} {self.due_date}"
            )
        self._set_customer_blocked_state(message=message, state="blocked")

    def action_set_paid(self):
        self.ensure_one()
        available_stage_ids = self.payment_method_id.stage_ids
        in_bank = available_stage_ids.filtered_domain([("type", "=", "in_bank")])
        write_vals = {"is_paid": "yes", "x_stage_id": in_bank.id}
        self._set_payment_state(write_vals=write_vals, state="yes")
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

    def action_set_unpaid(self):
        """
        1) reset the payment to draft
        2) cancel the payment
        3) set is_unpaid to True
        :return: None
        """
        self.ensure_one()
        self.action_draft()
        self.action_cancel()
        available_stage_ids = self._get_available_stages()
        unpaid_stage = available_stage_ids.filtered_domain([("type", "=", "unpaid")])
        if unpaid_stage:
            self.x_stage_id = unpaid_stage
        self.is_unpaid = "yes"
        message = f"Blocage suite impayé {self.name}"
        if self.transaction_number:
            message += (
                f" {self.payment_method_name} {self.transaction_number} {self.due_date}"
            )
        self._set_customer_blocked_state(message=message, state="blocked")

    def _set_customer_blocked_state(self, message: str, state: str) -> None:
        """
        set x_customer_blocked to True or False depends on the state
        and create a partner_block_history record
        :param message: message to write in blocking history of the partner
        :param state: blocked or unblocked
        :return: None
        """
        ir_module_obj = self.env["ir.module.module"].sudo()
        module_id = ir_module_obj.search(
            [
                ("name", "=", "v__block_unpaid_customers"),
                ("state", "=", "installed"),
            ],
            limit=1,
        )
        # No need to block partner if the payment is outbound
        if (
            module_id
            and self.env.company.x_block_unpaid_customer
            and self.payment_type == "inbound"
        ):
            self.partner_id.partner_block_history_ids = [
                (
                    0,
                    0,
                    {
                        "date": fields.datetime.utcnow(),
                        "description": message,
                        "state": state,
                    },
                )
            ]
            self.partner_id.x_customer_blocked = True if state == "blocked" else False

    def action_open_related_payments(self):
        self.ensure_one()
        action = {
            "name": "Remplacements",
            "view_mode": "tree,form",
            "res_model": "account.payment",
            "type": "ir.actions.act_window",
            "domain": [
                (
                    "id",
                    "in",
                    self.replacement_payment_ids.ids,
                )
            ],
            "context": {"create": 0},
            "target": "self",
        }
        return action

    def action_replace_payment(self):
        to_replace_payments = self.filtered(
            lambda payment: (
                payment.is_unpaid == "yes" or payment.is_butterfly == "yes"
            )
            and payment.state == "cancel"
        )

        if len(set(to_replace_payments.mapped("partner_type"))) > 1:
            raise exceptions.ValidationError("Les paiements doivent être du même type")
        if len(set(to_replace_payments.mapped("partner_id"))) > 1:
            raise exceptions.ValidationError(
                "Les paiements doivent partager le même partenaire"
            )

        if not to_replace_payments:
            return

        invoice_ids = to_replace_payments.x_to_reconcile_line_ids.move_id.filtered(
            lambda move: move.is_invoice()
        )
        replacement_amount = sum(to_replace_payments.mapped("replaced_amount"))
        original_amount = sum(to_replace_payments.mapped("amount"))
        action = invoice_ids.action_register_payment()
        action["context"].update(
            {
                "original_payment_ids": to_replace_payments.ids,
                "dont_redirect_to_payments": True,
                "default_amount": original_amount - replacement_amount,
            }
        )
        return action

    def _set_payment_state(self, write_vals: dict, state: str) -> None:
        """
        Set is_butterfly or is_prior_notice or is_unpaid, to fixed or yes.
        Is the current state is yes set it to fixed
        else if the state is fixed set it to yes
        :param: state: fixed or yes
        :param: write_vals: dict contains the values to update
        :return: None
        """
        # to avoid complexity score and use three condition statements
        # we iterate through each one of them
        # and change the desired field
        opposite_state = "fixed" if state == "yes" else "yes"
        concerned_fields = ("is_butterfly", "is_prior_notice", "is_unpaid")
        for field in concerned_fields:
            if self[field] == state:
                write_vals[field] = opposite_state
        self.write(write_vals)

    @api.model_create_multi
    def create(self, vals_list):
        res = super(AccountPayment, self).create(vals_list)
        for payment in res:
            payment._toggle_is_paid()
        return res

    def _toggle_is_paid(self) -> None:
        """
        if we got on of those stages type
        we simply let the user decide
        if the payment is_paid or not, through the button
        :return: None
        """
        self.ensure_one()
        stages = self._get_available_stages().filtered_domain(
            [("type", "in", ("butterfly", "prior_notice", "unpaid"))]
        )
        self.is_paid = not stages

    def write(self, vals):
        if "payment_method_line_id" in vals:
            for payment in self:
                payment._toggle_is_paid()

        return super(AccountPayment, self).write(vals)

    @api.ondelete(at_uninstall=False)
    def _on_delete_replacement(self):
        for payment in self:
            replacement_amount = payment.amount
            for original_payment_id in payment.original_payment_ids.sorted(
                lambda pay: (pay.replaced_amount, pay.id)
            ):
                # reset the replaced_amount after the deletion of the replacement
                new_amount = original_payment_id.replaced_amount - replacement_amount
                original_payment_id.replaced_amount = (
                    new_amount if new_amount >= 0 else 0
                )
                replacement_amount = abs(new_amount)
                if original_payment_id.replaced_amount < original_payment_id.amount:
                    original_payment_id._set_payment_state(
                        write_vals={"is_replaced": False, "is_paid": False},
                        state="fixed",
                    )
                    message = (
                        f"Blocage suite suppression de remplacement {payment.name}"
                    )
                    if payment.transaction_number:
                        message += (
                            f" - {payment.payment_method_name} "
                            f"{payment.transaction_number} {payment.due_date}"
                        )
                    self._set_customer_blocked_state(message=message, state="blocked")
