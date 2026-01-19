from odoo import fields, models


class WithholdingTax(models.Model):
    _name = "withholding.tax"
    _description = "Retenue à la source"

    name = fields.Char(string="Nom", required=True, copy=False)
    percentage = fields.Float(string="Taux", required=True)
    journal_id = fields.Many2one(
        string="Journal", comodel_name="account.journal", required=True
    )
    account_id = fields.Many2one(
        string="Compte", comodel_name="account.account", required=True
    )
    company_id = fields.Many2one(
        string="Societé",
        comodel_name="res.company",
        default=lambda self: self.env.company,
    )
    type = fields.Selection(
        string="Porté",
        selection=[("inbound", "Vente"), ("outbound", "Achat")],
        required=True,
    )
