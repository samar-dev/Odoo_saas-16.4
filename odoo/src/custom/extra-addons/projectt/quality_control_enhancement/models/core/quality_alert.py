from odoo import fields, models, api


class QualityAlert(models.Model):
    _inherit = "quality.alert"

    picking_product_tmpl_ids = fields.Many2many(
        comodel_name="product.template",
        string=" product_tmpl_ids",
        relation="quality_alert_product_template_rel",
        compute="_compute_picking_product_tmpl_ids",
    )

    @api.depends("picking_id")
    def _compute_picking_product_tmpl_ids(self):
        for quality in self:
            if quality.picking_id:
                move_ids_without_package = quality.picking_id.move_ids_without_package
                quality.picking_product_tmpl_ids = (
                    move_ids_without_package.product_id.product_tmpl_id
                )
            else:
                quality.picking_product_tmpl_ids = self.env["product.template"].search(
                    []
                )
