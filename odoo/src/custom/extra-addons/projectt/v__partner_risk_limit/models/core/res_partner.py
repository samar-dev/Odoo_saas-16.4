from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    x_risk_limit = fields.Float(
        string="Risque",
        company_dependent=True,
        copy=False,
        readonly=False,
        tracking=True,
    )
    x_use_risk_limit = fields.Boolean(
        string="Risque",
        compute="_compute_x_use_risk_limit",
        inverse="_inverse_x_use_risk_limit",
    )
    x_show_risk_limit = fields.Boolean(
        string="Blocage par risque",
        default=lambda self: self.env.company.x_use_risk_limit,
        compute="_compute_x_show_risk_limit",
    )
    x_risk_limit_readonly = fields.Boolean(compute="_compute_x_risk_limit_readonly")
    x_current_risk_amount = fields.Float(
        string="Risque actuel", compute="_compute_x_current_risk_amount"
    )

    @api.depends_context("company")
    def _compute_x_use_risk_limit(self):
        for partner in self:
            company_limit = self.env["ir.property"]._get("x_risk_limit", "res.partner")
            partner.x_use_risk_limit = partner.x_risk_limit != company_limit

    def _inverse_x_use_risk_limit(self):
        for partner in self:
            if not partner.x_use_risk_limit:
                partner.x_risk_limit = self.env["ir.property"]._get(
                    "x_risk_limit", "res.partner"
                )

    @api.depends_context("company")
    def _compute_x_show_risk_limit(self):
        for partner in self:
            partner.x_show_risk_limit = self.env.company.x_use_risk_limit

    def _compute_x_risk_limit_readonly(self):
        for partner in self:
            partner.x_risk_limit_readonly = not self.env.user.has_group(
                "v__partner_risk_limit.group_edit_risk_limit"
            )

    def _compute_x_current_risk_amount(self):
        account_move_sudo = self.env["account.move"].sudo()
        account_payment_sudo = self.env["account.payment"].sudo()
        for partner in self:
            current_credit = partner.x_current_outstanding_amount
            invoice_domain = [
                ("partner_id", "=", partner.id),
                ("move_type", "=", "out_invoice"),
                ("company_id", "=", self.env.company.id),
                ("state", "=", "draft"),
            ]
            # payments not paid yet and not replaced
            # they can be partially replaced
            payment_one = [
                ("partner_id", "=", partner.id),
                ("payment_type", "=", "inbound"),
                ("partner_type", "=", "customer"),
                ("company_id", "=", self.env.company.id),
                ("state", "=", "posted"),
                ("is_paid", "=", False),
                ("is_replaced", "=", False),
            ]
            total_draft_invoices = account_move_sudo.read_group(
                domain=invoice_domain,
                fields=["total:sum(amount_total)"],
                groupby="partner_id",
            )
            total_draft_invoices = (
                total_draft_invoices and total_draft_invoices[0].get("total", 0) or 0
            )
            total_payments = account_payment_sudo.read_group(
                domain=payment_one,
                fields=[
                    "total_amount:sum(amount)",
                    "total_replaced_amount:sum(replaced_amount)",
                ],
                groupby="partner_id",
            )
            total_payments_amount = (
                total_payments and total_payments[0].get("total_amount", 0) or 0
            )
            total_payments_replaced_amount = (
                total_payments
                and total_payments[0].get("total_replaced_amount", 0)
                or 0
            )
            # as long as payments can be partially replaced,
            # and we are not marking them as replaced
            # we will simply subtract the replaced amount from the total amount
            total_payments = total_payments_amount - total_payments_replaced_amount
            partner.x_current_risk_amount = (
                current_credit + total_draft_invoices + total_payments
            )
