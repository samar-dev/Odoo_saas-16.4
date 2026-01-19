from odoo import models, fields


class Store(models.Model):
    _name = "res.partner.store"
    _description = "Store"

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code")
    position = fields.Char(string="Position")
    address = fields.Char(string="Address")
    partner_id = fields.Many2one("res.partner", string="Partner")
    product_ids = fields.Many2many("product.template", string="Products in Store")
