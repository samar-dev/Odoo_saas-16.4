from odoo import models, fields, api


class TreasuryTemplate(models.Model):
    _name = "treasury.template"
    _description = "Treasury Template"

    name = fields.Char(string="Treasury Name", required=True)

    treasury_line_ids = fields.Many2many(
        "purchase.treasury",
        string="Treasury Lines",
        default=lambda self: self._default_treasury_lines(),
    )

    @api.model
    def _default_treasury_lines(self):
        # Optional: filter out lines with no sector
        return (
            self.env["purchase.treasury"]
            .search([("sector_id.setor_parent_id", "!=", False)])
            .ids
        )
