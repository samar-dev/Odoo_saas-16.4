from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = "account.move"

    invoice_line_ids = (
        fields.One2many(  # /!\ invoice_line_ids is just a subset of line_ids.
            "account.move.line",
            "move_id",
            string="Invoice lines",
            copy=False,
            readonly=False,
            domain=[("display_type", "in", ("product", "line_section", "line_note"))],
        )
    )
