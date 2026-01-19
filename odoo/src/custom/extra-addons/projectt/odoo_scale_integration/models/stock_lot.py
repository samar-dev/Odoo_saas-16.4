from odoo import models, fields

class StockLot(models.Model):
    _inherit = "stock.lot"

    numero_adm = fields.Char(string="N°ADM")
    ac = fields.Char(string="AC")
    k_two = fields.Float(string="K232", digits=(16, 3))
    k_seven = fields.Float(string="K270", digits=(16, 3))
    pesticides = fields.Float(string="Pesticides", digits=(16, 3))