from odoo import fields, models, api


class AccountJournal(models.Model):
    _inherit = "account.journal"

    x_rapp_date = fields.Date(string="Date de rapprochement")
    def action_open_bank_mouvements(self):
        return {
            "name": "Mouvements du banque",
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "res_model": "bank.movement",
            "domain": [('journal_id', '=', self.id)],
            "context": {
                'default_journal_id': self.id,
            },
        }
    def action_open_bank_statement(self):
        return {
            "name": "Releve bancaire",
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "res_model": "bank.statement",
            "domain": [('journal_id', '=', self.id)],
            "context": {
                'default_journal_id': self.id,
            },
        }
