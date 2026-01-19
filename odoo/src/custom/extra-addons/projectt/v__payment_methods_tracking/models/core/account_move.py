from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    x_payment_id = fields.Many2one(comodel_name="account.payment")
