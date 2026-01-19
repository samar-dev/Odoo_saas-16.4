from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    use_production_date = fields.Boolean(string="Use Production Date")
    config_production_date = fields.Boolean(compute="_compute_config_production_date")

    def _compute_config_production_date(self):
        config_production_date = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("production_date.config_production_date")
        )
        for product in self:
            product.config_production_date = config_production_date
