from odoo import models, fields, _


class ManufacturingOrder(models.Model):
    _inherit = "mrp.production"

    parent_workcenter_id = fields.Many2one(
        related="workcenter_id.workcenter_id", store=True
    )
    mrp_production_id = fields.Many2one(
        comodel_name="mrp.production", string=_("Mix order")
    )

    # Overite onchange method
    def _onchange_product_id(self):
        pass
