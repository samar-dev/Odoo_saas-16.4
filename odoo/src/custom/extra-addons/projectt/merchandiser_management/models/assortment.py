from odoo import api, fields, models


class Assortment(models.Model):
    _name = "assortment"
    _description = "Assortment"

    # Basic info
    name = fields.Char(string="Name", required=True)
    partner_id = fields.Many2one("res.partner", string="Partner")

    # Address fields
    street = fields.Char(related="partner_id.street", store=True, readonly=True)
    street2 = fields.Char(related="partner_id.street2", store=True, readonly=True)
    zip = fields.Char(related="partner_id.zip", store=True, readonly=True)
    city = fields.Char(related="partner_id.city", store=True, readonly=True)
    state_id = fields.Many2one(related="partner_id.state_id", store=True, readonly=True)
    country_id = fields.Many2one(
        related="partner_id.country_id", store=True, readonly=True
    )

    # Product Templates
    product_template_ids = fields.Many2many(
        comodel_name="product.template",
        relation="assortment_product_template_rel",
        string="Product Templates",
    )

    # Counts
    assortment_product_templates_count = fields.Integer(
        compute="_compute_assortment_product_templates_count", string="Templates"
    )
    assortment_products_count = fields.Integer(
        compute="_compute_assortment_products_count", string="Products"
    )

    @api.depends("product_template_ids")
    def _compute_assortment_product_templates_count(self):
        for record in self:
            record.assortment_product_templates_count = len(record.product_template_ids)

    @api.depends("product_template_ids")
    def _compute_assortment_products_count(self):
        # You can count templates or their variants here
        for record in self:
            record.assortment_products_count = len(record.product_template_ids)

    # Stores where templates exist
    product_store_ids = fields.Many2many(
        "res.partner.store", string="Stores", compute="_compute_product_store_ids"
    )

    @api.depends("product_template_ids")
    def _compute_product_store_ids(self):
        for record in self:
            stores = self.env["res.partner.store"]
            for template in record.product_template_ids:
                stores |= self.env["res.partner.store"].search(
                    [("product_ids", "in", template.ids)]
                )
            record.product_store_ids = stores

    # -----------------------
    # Actions
    # -----------------------
    def action_open_assortment_product_templates(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "product.template",
            "views": [
                [self.env.ref("product.product_template_kanban_view").id, "kanban"],
                [self.env.ref("product.product_template_tree_view").id, "tree"],
                [self.env.ref("product.product_template_only_form_view").id, "form"],
            ],
            "domain": [("id", "in", self.product_template_ids.ids)],
            "context": {"create": False},
            "name": "Assortment Product Templates",
        }

    def action_open_assortment_stores(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "res.partner.store",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [("id", "in", self.product_store_ids.ids)],
            "name": "Stores",
        }
