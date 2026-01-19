from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    x_account_use_credit_limit = fields.Boolean(
        string="Blocage par encours",
        related="company_id.x_account_use_credit_limit",
        readonly=False,
    )

    x_account_default_credit_limit = fields.Monetary(
        string="Plafond d'encours",
        readonly=False,
        compute="_compute_x_account_default_credit_limit",
        inverse="_inverse_x_account_default_credit_limit",
    )

    @api.depends("company_id")
    def _compute_x_account_default_credit_limit(self):
        for setting in self:
            setting.x_account_default_credit_limit = self.env["ir.property"]._get(
                "x_credit_limit", "res.partner"
            )

    def _inverse_x_account_default_credit_limit(self):
        for setting in self:
            self.env["ir.property"]._set_default(
                "x_credit_limit",
                "res.partner",
                setting.x_account_default_credit_limit,
                self.company_id.id,
            )
