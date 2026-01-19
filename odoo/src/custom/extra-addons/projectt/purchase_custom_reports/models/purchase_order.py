from odoo import models, fields, api, _


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    bat_date = fields.Date(string="Date BAT", default=False)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    industry_id = fields.Many2one(
        comodel_name="res.partner.industry",
        string="Secteur d'activité",
        related="partner_id.industry_id",
        store=True,
    )


class AccountMove(models.Model):
    _inherit = "account.move"

    industry_id = fields.Many2one(
        comodel_name="res.partner.industry",
        string="Secteur d'activité",
        related="partner_id.industry_id",
        store=True,
        readonly=True,
    )
