from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    assortment_id = fields.Many2one("assortment", string="Assortment")
    x_customer_blocked = fields.Boolean(string="Customer Blocked")

    store_ids = fields.Many2many(
        "res.partner.store",  # model we link to
        "res_partner_store_rel",  # name of the relation table in the DB
        "partner_id",  # column for res.partner id
        "store_id",  # column for store id
        string="Magasin",  # label on the form
        domain=lambda self: [("partner_id", "=", self.id)],
    )

    def action_create_assortment(self):
        active_ids = self.env.context.get("active_ids")
        for partner in self.browse(active_ids):
            if partner.child_ids.filtered(lambda p: p.type == "other"):
                for child in partner.child_ids.filtered(lambda p: p.type == "other"):
                    assortment_id = self.env["assortment"].create(
                        {
                            "name": str(partner.name) + "-" + str(child.state_id.name),
                            "partner_id": child.id,
                        }
                    )
                    child.assortment_id = assortment_id.id
