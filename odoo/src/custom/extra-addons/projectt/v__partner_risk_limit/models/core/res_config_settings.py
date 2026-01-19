from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    x_use_risk_limit = fields.Boolean(
        string="Blocage par risque",
        related="company_id.x_use_risk_limit",
        readonly=False,
    )

    x_default_risk_limit = fields.Monetary(
        string="Plafond de risque",
        readonly=False,
        compute="_compute_x_default_risk_limit",
        inverse="_inverse_x_default_risk_limit",
    )

    @api.depends("company_id")
    def _compute_x_default_risk_limit(self):
        for setting in self:
            setting.x_default_risk_limit = self.env["ir.property"]._get(
                "x_risk_limit", "res.partner"
            )

    def _inverse_x_default_risk_limit(self):
        for setting in self:
            self.env["ir.property"]._set_default(
                "x_risk_limit",
                "res.partner",
                setting.x_default_risk_limit,
                self.company_id.id,
            )
