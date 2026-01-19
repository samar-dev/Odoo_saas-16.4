from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    x_invoice_limit = fields.Integer(
        string="Plafond Factures",
        company_dependent=True,
        copy=False,
        readonly=False,
        tracking=True,
    )
    x_use_partner_invoice_limit = fields.Boolean(
        string="Plafond Factures",
        compute="_compute_x_use_partner_invoice_limit",
        inverse="_inverse_x_use_partner_invoice_limit",
    )
    x_show_invoice_limit = fields.Boolean(
        string="Blocage par facture",
        default=lambda self: self.env.company.x_use_invoice_limit,
        compute="_compute_x_show_invoice_limit",
    )
    x_invoice_limit_readonly = fields.Boolean(
        compute="_compute_x_invoice_limit_readonly"
    )
    x_current_invoice_limit = fields.Integer(
        string="Facture non payée", compute="_compute_x_current_invoice_limit"
    )

    @api.depends_context("company")
    def _compute_x_use_partner_invoice_limit(self):
        for partner in self:
            company_limit = self.env["ir.property"]._get(
                "x_invoice_limit", "res.partner"
            )
            partner.x_use_partner_invoice_limit = (
                partner.x_invoice_limit != company_limit
            )

    def _inverse_x_use_partner_invoice_limit(self):
        for partner in self:
            if not partner.x_use_partner_invoice_limit:
                partner.x_invoice_limit = self.env["ir.property"]._get(
                    "x_invoice_limit", "res.partner"
                )

    @api.depends_context("company")
    def _compute_x_show_invoice_limit(self):
        for partner in self:
            partner.x_show_invoice_limit = self.env.company.x_use_invoice_limit

    def _compute_x_invoice_limit_readonly(self):
        for partner in self:
            partner.x_invoice_limit_readonly = not self.env.user.has_group(
                "v__partner_invoice_limit.group_edit_invoice_limit"
            )

    def _compute_x_current_invoice_limit(self):
        account_move_sudo = self.env["account.move"].sudo()
        for partner in self:
            invoice_domain = [
                ("partner_id", "=", partner.id),
                ("move_type", "=", "out_invoice"),
                ("company_id", "=", self.env.company.id),
                ("state", "=", "posted"),
                ("payment_state", "in", ("not_paid", "partial")),
            ]

            total_invoices = account_move_sudo.search_count(invoice_domain)
            partner.x_current_invoice_limit = total_invoices
