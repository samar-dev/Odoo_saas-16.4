from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_taxable = fields.Boolean(
        string="Timbre Autorisé", default=True, copy=False, tracking=True
    )
