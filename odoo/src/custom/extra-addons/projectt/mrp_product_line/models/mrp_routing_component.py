from odoo import fields, models, api, _


class MrpRoutingComponent(models.Model):
    _name = "mrp.routing.component"
    _description = "Product Line Component"

    product_id = fields.Many2one(comodel_name="product.product", string=_("Component"))
    product_qty = fields.Float(string=_("Quantity"), default=1)
    product_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Unit of Measure",
        required=True,
        compute="_compute_product_uom_id",
        store=True,
        readonly=False,
        precompute=True,
    )
    mrp_routing_id = fields.Many2one(comodel_name="mrp.routing")

    @api.depends("product_id")
    def _compute_product_uom_id(self):
        """Changes UoM if product_id changes."""
        for record in self:
            record.product_uom_id = record.product_id.uom_id.id
