from odoo import api, exceptions, fields, models


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    # check fields
    customer_bank = fields.Char(string="Banque Client")
    customer_bank_id = fields.Many2one(
        string="Banque Client",
        comodel_name="res.partner.bank",
        domain="[('partner_id', '=', partner_id)]",
        compute="_compute_customer_bank_id",
        readonly=False,
        store=True,
    )
    check_certified = fields.Boolean(string="Chèque Certifié")
    confirmation_number = fields.Char(string="Numéro Confirmation", copy=False)

    # check, banknote fields
    transaction_number = fields.Char(string="Numéro de la valeur")
    due_date = fields.Date(string="Date d'échéance")
    due_in_days = fields.Integer(
        string="Echéance en jours", compute="_compute_due_in_days"
    )

    # bank transfer fields
    from_account_id = fields.Many2one(
        string="Compte expéditeur", comodel_name="res.partner.bank"
    )
    to_account_id = fields.Many2one(
        string="Compte du destinataire", comodel_name="res.partner.bank"
    )
    x_attachement_ids = fields.Many2many(
        string="Attachements", comodel_name="ir.attachment"
    )

    @api.depends("partner_id")
    def _compute_customer_bank_id(self):
        for payment in self:
            if (
                not payment.customer_bank_id
                or payment.customer_bank_id.partner_id != payment.partner_id
            ):
                payment.customer_bank_id = fields.first(payment.partner_id.bank_ids)

    @api.depends("payment_date", "due_date")
    def _compute_due_in_days(self):
        for record in self:
            now = record.payment_date
            later = record.due_date
            record.due_in_days = 0
            if now and later:
                record.due_in_days = (later - now).days

    # noinspection PyUnresolvedReferences
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

    @api.constrains("payment_date")
    def _check_for_payment_date(self):
        # payment date can't be in the future
        for record in self:
            if record.payment_date > fields.date.today():
                raise exceptions.ValidationError(
                    "La date de paiement ne peut pas être postérieure"
                )

    @api.constrains("due_date")
    def _check_for_due_date(self):
        """
        Due date must be the same as the payment_date or after it
        :return: None
        """
        for record in self:
            if record.due_in_days < 0:
                raise exceptions.ValidationError(
                    "L'échéance en jours ne peut pas être négative."
                )

    @api.onchange("payment_method_line_id")
    def _check_for_stage_ids(self):
        if self.payment_method_code in (
            "v-check",
            "v-banknote",
            "v-cash",
            "v-transfer",
        ):
            if not self.payment_method_line_id.payment_method_id.stage_ids:
                raise exceptions.ValidationError(
                    "Le moyen de paiement doit avoir au moins une étape"
                )

    def _get_custom_fields(self):
        res = {
            "transaction_number": self.transaction_number,
            "due_date": self.due_date,
            "check_certified": self.check_certified,
            "confirmation_number": self.confirmation_number,
            "from_account_id": self.from_account_id.id,
            "to_account_id": self.to_account_id.id,
            "x_auto_created": True,
            "customer_bank_id": self.customer_bank_id.id,
        }
        return res

    def _create_payment_vals_from_wizard(self, batch_result):
        res = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard(
            batch_result
        )
        # pass our customized fields from the wizard to account_payment
        res.update(self._get_custom_fields())
        return res

    def _create_payment_vals_from_batch(self, batch_result):
        res = super(AccountPaymentRegister, self)._create_payment_vals_from_batch(
            batch_result
        )
        # pass our customized fields from the wizard to account_payment
        res.update(self._get_custom_fields())
        return res

    def _get_customized_payment_methods(self):
        return [
            "v-check",
            "v-banknote",
            "v-cash",
            "v-transfer",
        ]

    def _reconcile_payments(self, to_process, edit_mode=False):
        if self.payment_method_code in self._get_customized_payment_methods():
            domain = [
                ("parent_state", "=", "posted"),
                ("account_type", "in", ("asset_receivable", "liability_payable")),
                ("reconciled", "=", False),
            ]
            for vals in to_process:
                payment_id = vals["payment"]
                payment_lines = payment_id.line_ids.filtered_domain(domain)
                lines = vals["to_reconcile"]

                for account in payment_lines.account_id:
                    payment_id.x_to_reconcile_line_ids = (
                        payment_lines + lines
                    ).filtered_domain(
                        [("account_id", "=", account.id), ("reconciled", "=", False)]
                    )
            return True

        return super(AccountPaymentRegister, self)._reconcile_payments(
            to_process, edit_mode
        )

    def _init_payments(self, to_process, edit_mode=False):
        payments = super(AccountPaymentRegister, self)._init_payments(
            to_process, edit_mode
        )
        for payment in payments:
            for attachment in self.x_attachement_ids:
                self.env["ir.attachment"].create(
                    {
                        "name": attachment.name,
                        "type": "binary",
                        "datas": attachment.datas,
                        "res_model": payment._name,
                        "res_id": payment.id,
                    }
                )
        return payments

    def _compute_amount(self):
        old_amount = self.amount
        res = super(AccountPaymentRegister, self)._compute_amount()
        if old_amount != 0:
            self.amount = old_amount
        return res
