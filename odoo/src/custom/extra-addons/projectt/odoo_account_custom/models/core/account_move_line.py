from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    x_account_reconcile = fields.Char(string="Lettrage Sage")
