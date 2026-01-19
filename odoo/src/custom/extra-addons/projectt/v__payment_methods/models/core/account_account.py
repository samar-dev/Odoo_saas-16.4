from odoo import fields, models


class AccountAccount(models.Model):
    _inherit = "account.account"

    is_partner_mandatory = fields.Boolean(string="Partenaire obligatoire")
