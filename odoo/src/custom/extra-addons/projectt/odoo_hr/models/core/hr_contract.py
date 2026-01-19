from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression
from datetime import datetime, timedelta


class HrContract(models.Model):
    _name = "hr.contract"
    _inherit = ["hr.contract", "mail.thread"]

    test_period_start = fields.Date(string="Début période d'essai", tracking=True)
    test_period_end = fields.Date(string="Fin période d'essai", tracking=True)
    wage = fields.Monetary(
        "Wage", required=False, tracking=True, help="Employee's monthly gross wage."
    )

    @api.constrains("employee_id", "state", "kanban_state", "date_start", "date_end")
    def _check_current_contract(self):
        """Two contracts in state [incoming | open | close] cannot overlap"""
        for contract in self.filtered(
            lambda c: (
                c.state not in ["draft", "cancel"]
                or c.state == "draft"
                and c.kanban_state == "done"
            )
            and c.employee_id
        ):
            domain = [
                ("id", "!=", contract.id),
                ("employee_id", "=", contract.employee_id.id),
                "|",
                ("state", "in", ["open"]),
                "&",
                ("state", "=", "draft"),
                ("kanban_state", "=", "done"),  # replaces incoming
            ]

            if not contract.date_end:
                start_domain = []
                end_domain = [
                    "|",
                    ("date_end", ">=", contract.date_start),
                    ("date_end", "=", False),
                ]
            else:
                start_domain = [("date_start", "<=", contract.date_end)]
                end_domain = [
                    "|",
                    ("date_end", ">", contract.date_start),
                    ("date_end", "=", False),
                ]

            domain = expression.AND([domain, start_domain, end_domain])
            if self.search_count(domain):
                raise ValidationError(
                    _(
                        "An employee can only have one contract"
                        " at the same time. (Excluding Draft and "
                        "Cancelled contracts)"
                    )
                )

    def check_active_contract(self):
        for s in self:
            contracts = s.employee_id.sudo().contract_ids.filtered(
                lambda c: c.state == "open" and c.id != s._origin.id
            )
            if contracts and len(contracts) > 0:
                raise ValidationError(
                    "Un même employée ne peut pas avoir"
                    " plus d'un contract actif par société"
                )

    def check_expiry(self):
        admin_group = self.env.ref("mrp.group_mrp_manager")
        user_ids = admin_group.users
        d = datetime.today() + timedelta(days=8)
        contracts = self.env["hr.contract"].search(
            [("state", "=", "open"), ("date_end", "<", d)]
        )
        if contracts and len(contracts) > 0 and user_ids:
            channel_name = "Contrats"
            message = "<p>Votre contrat : "
            message += f'<a href="#" data-oe-model="{self._name}" data-oe-id'
            message += f'="{self.id}">{self.name}</a><br/>'
            message += "a expiré, veuillez vérifier et renouveler le contrat auprès du service concerné.</p>"
            self._base_send_a_message(user_ids, channel_name, message)
            return self._base_display_notification(
                title=channel_name,
                type="error",
                message="Le contrat a expiré, une action est requise.",
                sticky=False,
            )
        else:
            return self._base_display_notification(
                type="warning",
                message="Impossible de trouver un administrateur de fabrication pour traiter cette demande.",
                sticky=False,
            )
