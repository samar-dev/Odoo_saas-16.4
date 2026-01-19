from odoo import fields, models


class AccountPaymentMethod(models.Model):
    _inherit = "account.payment.method"

    is_printable = fields.Boolean(string="Est imprimable", default=False)
