from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    x_use_invoice_limit = fields.Boolean(
        string="Blocage par facture",
        related="company_id.x_use_invoice_limit",
        readonly=False,
    )

    x_default_invoice_limit = fields.Integer(
        string="Plafond de facture",
        readonly=False,
        compute="_compute_x_default_invoice_limit",
        inverse="_inverse_x_default_invoice_limit",
    )

    @api.depends("company_id")
    def _compute_x_default_invoice_limit(self):
        for setting in self:
            setting.x_default_invoice_limit = (
                self.env["ir.property"]._get("x_invoice_limit", "res.partner") or 1
            )

    def _inverse_x_default_invoice_limit(self):
        for setting in self:
            self.env["ir.property"]._set_default(
                "x_invoice_limit",
                "res.partner",
                setting.x_default_invoice_limit,
                self.company_id.id,
            )
