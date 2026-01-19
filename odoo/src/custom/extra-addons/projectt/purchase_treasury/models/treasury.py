from odoo import models, fields


class PurchaseTreasury(models.Model):
    _name = "purchase.treasury"
    _description = "Purchase Treasury"

    name = fields.Char(string="Label", required=True)
    sector_id = fields.Many2one("purchase.sector", string="Sector")
    category = fields.Char(string="Category")
    amount = fields.Float(string="Amount")
    account_ids = fields.Many2many("account.account", string="Accounts")
    date = fields.Date(string="Date")

    account_treasury_ids = fields.Many2many(
        "account.treasury", string="Treasury Accounts"
    )


class AccountTreasury(models.Model):
    _name = "account.treasury"
    _description = "Treasury Account Mapping"

    name = fields.Char(string="Name")
    account_id = fields.Many2one("account.account", string="Account", required=True)
    sens = fields.Selection(
        [
            ("debit", "Débit"),
            ("credit", "Crédit"),
        ],
        string="Sens",
        required=True,
    )
    journal_ids = fields.Many2many("account.journal", string="Journals")
