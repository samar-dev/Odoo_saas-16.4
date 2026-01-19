from odoo import fields, models


class PartnerBlockHistory(models.Model):
    _name = "partner.block.history"
    _order = "date desc, id desc"

    partner_id = fields.Many2one(string="Client", comodel_name="res.partner")
    company_id = fields.Many2one(
        comodel_name="res.company", default=lambda self: self.env.company
    )
    date = fields.Datetime(string="Date", required=True, default=fields.Datetime.now)
    description = fields.Char(string="Déscription", required=True)
    state = fields.Selection(
        selection=[("blocked", "Bloqué"), ("unblocked", "Débloqué")],
        required=True,
        default="blocked",
    )
