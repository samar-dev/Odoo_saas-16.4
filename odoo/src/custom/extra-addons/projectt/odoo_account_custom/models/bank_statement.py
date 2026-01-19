from odoo import fields, models, api


class BankStament(models.Model):
    _name = 'bank.statement'
    _description = 'Bank Statement'

    name = fields.Char(string="Libellé")
    date = fields.Date(string="Date")
    debit = fields.Monetary(string="Debit")
    credit = fields.Monetary(string="Crédit")
    currency_id = fields.Many2one(comodel_name="res.currency")
    journal_id = fields.Many2one(comodel_name="account.journal")

    def action_unlink(self):
        self.unlink()
