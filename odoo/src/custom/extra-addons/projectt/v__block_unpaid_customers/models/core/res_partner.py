from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    x_customer_blocked = fields.Boolean(
        string="Client Bloqué",
        company_dependent=True,
        copy=False,
        readonly=False,
    )
    partner_block_history_ids = fields.One2many(
        comodel_name="partner.block.history", inverse_name="partner_id"
    )
    x_show_block_unpaid_customer = fields.Boolean(
        default=lambda self: self.env.company.x_block_unpaid_customer,
        compute="_compute_x_show_block_unpaid_customer",
    )

    def _compute_x_show_block_unpaid_customer(self):
        for partner in self:
            partner.x_show_block_unpaid_customer = (
                self.env.company.x_block_unpaid_customer
            )

    def action_toggle_x_customer_blocked(self):
        if self.env.user.has_group(
            "v__block_unpaid_customers.group_block_unpaid_customers"
        ):
            self.x_customer_blocked = not self.x_customer_blocked
            messages = {
                True: f"Blocage Client par {self.env.user.name}.",
                False: f"Déblocage Client par {self.env.user.name}",
            }
            self.partner_block_history_ids = [
                (
                    0,
                    0,
                    {
                        "date": fields.datetime.utcnow(),
                        "description": messages.get(self.x_customer_blocked),
                        "state": "blocked" if self.x_customer_blocked else "unblocked",
                    },
                )
            ]
