from odoo import fields, models


class AssortmentWizard(models.TransientModel):
    _name = "assortment.wizard"

    assortment_id = fields.Many2one("assortment", string="Assortment")
    date_assortment = fields.Date(string="Date")
    partner_id = fields.Many2one("res.partner", string="Partner")
    store_ids = fields.Many2many(
        "res.partner.store", string="Stores", compute="_compute_store_ids"
    )

    def action_add_assortment(self):
        active_ids = self.env.context.get("active_ids")
        for product in self.env["product.product"].browse(active_ids):
            product.write({"assortment_ids": [(4, self.assortment_id.id)]})
