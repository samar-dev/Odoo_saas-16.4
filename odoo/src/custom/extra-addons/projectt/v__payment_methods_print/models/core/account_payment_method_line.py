from odoo import fields, models


class AccountPaymentMethodLine(models.Model):
    _inherit = "account.payment.method.line"

    qweb_template_id = fields.Many2one(
        string="Modèle de rapport",
        comodel_name="ir.ui.view",
        domain=[("type", "=", "qweb")],
    )
    report_paperformat_id = fields.Many2one(
        string="Format Papier", comodel_name="report.paperformat"
    )
