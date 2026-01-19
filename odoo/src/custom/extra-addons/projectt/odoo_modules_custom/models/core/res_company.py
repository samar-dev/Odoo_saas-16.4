from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    # Added field
    is_blocked = fields.Boolean(string="est bloqué")
    have_currency = fields.Boolean(string="Controle devise")
    blocked_year_ids = fields.One2many(
        "res.company.blocked.year",
        "company_id",
        string="Blocked Years"
    )
