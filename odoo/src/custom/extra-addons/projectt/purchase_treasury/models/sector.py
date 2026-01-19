from odoo import models, fields


class PurchaseSector(models.Model):
    _name = "purchase.sector"
    _description = "Purchase Sector"

    name = fields.Char(string="Sector Name", required=True)
    setor_parent_id = fields.Many2one("purchase.sector", string="Parent Sector")
