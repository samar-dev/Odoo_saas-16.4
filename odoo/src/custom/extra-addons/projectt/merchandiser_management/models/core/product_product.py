from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    assortment_ids = fields.Many2many(
        string="Assortments",
        comodel_name="assortment",
        relation="assortment_product_product_rel",
    )
    store_ids = fields.Many2many(
        "res.partner.store",
        string="Stores",
    )

    def button_add_assortment(self):
        return {
            "name": "Add to an assortment",
            "view_mode": "form",
            "res_model": "assortment.wizard",
            "view_id": self.env.ref(
                "merchandiser_management.view_assortment_wizard_form"
            ).id,
            "type": "ir.actions.act_window",
            "context": {
                "active_ids": self.ids,
            },
            "target": "new",
        }
