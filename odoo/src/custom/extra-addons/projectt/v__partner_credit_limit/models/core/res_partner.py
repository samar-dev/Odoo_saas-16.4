from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    x_credit_limit = fields.Float(
        string="Encours",
        company_dependent=True,
        copy=False,
        readonly=False,
        tracking=True,
    )
    x_use_partner_credit_limit = fields.Boolean(
        string="Encours",
        compute="_compute_x_use_partner_credit_limit",
        inverse="_inverse_x_use_partner_credit_limit",
    )
    x_show_credit_limit = fields.Boolean(
        string="Blocage par encours",
        default=lambda self: self.env.company.x_account_use_credit_limit,
        compute="_compute_x_show_credit_limit",
    )
    x_credit_limit_readonly = fields.Boolean(compute="_compute_x_credit_limit_readonly")
    x_current_outstanding_amount = fields.Float(
        string="Encours actuel", compute="_compute_x_current_outstanding_amount"
    )

    @api.depends_context("company")
    def _compute_x_use_partner_credit_limit(self):
        for partner in self:
            company_limit = self.env["ir.property"]._get(
                "x_credit_limit", "res.partner"
            )
            partner.x_use_partner_credit_limit = partner.x_credit_limit != company_limit

    def _inverse_x_use_partner_credit_limit(self):
        for partner in self:
            if not partner.x_use_partner_credit_limit:
                partner.x_credit_limit = self.env["ir.property"]._get(
                    "x_credit_limit", "res.partner"
                )

    @api.depends_context("company")
    def _compute_x_show_credit_limit(self):
        for partner in self:
            partner.x_show_credit_limit = self.env.company.x_account_use_credit_limit

    def _compute_x_credit_limit_readonly(self):
        for partner in self:
            partner.x_credit_limit_readonly = not self.env.user.has_group(
                "v__partner_credit_limit.group_edit_credit_limit"
            )

    def _compute_x_current_outstanding_amount(self):
        account_move_sudo = self.env["account.move"].sudo()
        account_payment_sudo = self.env["account.payment"].sudo()
        for partner in self:
            invoice_domain = [
                ("partner_id", "=", partner.id),
                ("move_type", "=", "out_invoice"),
                ("company_id", "=", self.env.company.id),
                ("state", "=", "posted"),
            ]
            refund_domain = [
                ("partner_id", "=", partner.id),
                ("move_type", "=", "out_refund"),
                ("company_id", "=", self.env.company.id),
                ("state", "=", "posted"),
            ]
            # all existing payments and not replaced
            # they can be partially replaced
            payment_domain = [
                ("partner_id", "=", partner.id),
                ("payment_type", "=", "inbound"),
                ("partner_type", "=", "customer"),
                ("company_id", "=", self.env.company.id),
                ("state", "=", "posted"),
                ("is_replaced", "=", False),
            ]
            total_invoices = account_move_sudo.read_group(
                domain=invoice_domain,
                fields=["total:sum(amount_total)"],
                groupby="partner_id",
            )
            total_invoices = total_invoices and total_invoices[0].get("total", 0) or 0

            total_refunds = account_move_sudo.read_group(
                domain=refund_domain,
                fields=["total:sum(amount_total)"],
                groupby="partner_id",
            )
            total_refunds = total_refunds and total_refunds[0].get("total", 0) or 0
            total_payments = account_payment_sudo.read_group(
                domain=payment_domain,
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
            partner.x_current_outstanding_amount = (
                total_invoices - total_refunds - total_payments
            )
