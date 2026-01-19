from odoo import models, fields, _


class PickingType(models.Model):
    _inherit = "stock.picking.type"

    allow_create_credit_note = fields.Boolean(
        string=_("Create credit note"),
        help="If checked,a credit note can be generated",
    )
