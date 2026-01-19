from odoo import models, fields

class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    categ_id = fields.Many2one('stock.scrap.categ', string="Scrap Category")
    note = fields.Text(string="Note")


class StockScrapCateg(models.Model):
    _name = 'stock.scrap.categ'
    _description = 'Scrap Category'

    name = fields.Char(string="Category Name", required=True)
    description = fields.Text(string="Description")
