from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    state = fields.Selection(
        string=_("State"),
        selection=[
            ("inactive", _("Inactive")),
            ("active", _("Active")),
        ],
        compute="_compute_state",
        store=True,
    )
    validator_ids = fields.One2many(
        comodel_name="res.partner.validator",
        inverse_name="partner_id",
        string=_("Validators"),
        required=False,
        tracking=True,
    )
    show_validation_button = fields.Boolean(
        string="Show validation button", compute="_compute_show_validation_button"
    )

    # -------------------------------------------------------------------------
    # COMPUTE METHODS
    # -------------------------------------------------------------------------

    def _populate_validators_from_templates(self):
        """Populate validators from template list if none exist."""
        for partner in self:
            if not partner.validator_ids:
                templates = self.env["res.partner.validator.list"].search([])
                for template in templates:
                    for user in template.validator_ids:
                        self.env["res.partner.validator"].create(
                            {
                                "partner_id": partner.id,
                                "validator_id": user.id,
                                "state": "waiting",
                            }
                        )

    def _compute_show_validation_button(self):
        for partner in self:
            partner.show_validation_button = False
            validator_id = self.validator_ids.filtered(
                lambda line: line.validator_id == self.env.user
            )
            if validator_id:
                if validator_id.state == "waiting":
                    partner.show_validation_button = True

    @api.depends("validator_ids", "validator_ids.state")
    def _compute_state(self):
        for partner in self.filtered(
            lambda partner: partner.supplier_rank == 1 or partner.customer_rank == 1
        ):
            partner.state = "inactive"
            if (
                not partner.validator_ids.filtered(
                    lambda line: line.state != "approved"
                )
                or not partner.validator_ids
            ):
                partner.state = "active"
                partner.active = True
            else:
                activity_ids = self.activity_ids
                partner.active = False
                self.activity_ids = activity_ids

    # -------------------------------------------------------------------------
    # LOW-LEVEL METHODS
    # -------------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):

        res = super().create(vals_list)
        for record in res:
            supplier_rank = res.supplier_rank
            customer_rank = res.customer_rank
            customer_company = res.is_company
            # Condition from your attrs: (supplier_rank == 0 or customer_rank == 0) and show_validation_button == False
            if supplier_rank == 0 and customer_rank == 0 and customer_company:
                raise ValidationError(
                    _(
                        "Partner cannot be created because it does not meet the required condition:\n"
                        "(supplier_rank = 0 OR customer_rank = 0)\n"
                        "Each service must create the corresponding customer or vendor in their own module."
                    )
                )
            record.send_notification()
        res._populate_validators_from_templates()
        return res

    def write(self, vals):
        res = super().write(vals)
        if "validator_ids" in vals:
            self.send_notification()
        return res

    # -------------------------------------------------------------------------
    # ACTION METHODS
    # -------------------------------------------------------------------------
    def action_validate(self):
        validator_id = self.validator_ids.filtered(
            lambda line: line.validator_id == self.env.user
        )
        if validator_id:
            self.validator_ids.write({'state': 'approved'})

    def action_refuse(self):
        validator_id = self.validator_ids.filtered(
            lambda line: line.validator_id == self.env.user
        )
        if validator_id:
            validator_id.state = "refused"

    # -------------------------------------------------------------------------
    # BUSINESS METHODS
    # -------------------------------------------------------------------------
    def send_notification(self):
        line_ids = self.validator_ids.filtered(lambda line: not line.notification_sent)
        if line_ids:
            validator_ids = line_ids.mapped("validator_id")
            channel_name = "Demande de Création"
            message = "<p>un nouveau client/fournisseur a été créé"
            message += " et en attente de validation: "
            message += f'<a href="#" data-oe-model="{self._name}" data-oe-id'
            message += f'="{self.id}">{self.name}</a></p>'
            self._base_send_a_message(validator_ids, channel_name, message)
            for line in line_ids:
                line.notification_sent = True
            return self._base_display_notification(
                title=channel_name,
                type="success",
                message="Votre demande a été envoyée avec succès",
                sticky=False,
            )
        else:
            return self._base_display_notification(
                title="Qualification des fournisseurs",
                type="warning",
                message="Impossible de trouver un validateur",
                sticky=False,
            )
