from odoo import _, api, fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    mrp_routing_ids = fields.Many2many(
        string=_("Product Line"), comodel_name="mrp.routing", tracking=True
    )
    product_tmpl_id = fields.Many2one(
        comodel_name="product.template",
        domain="['&', ('is_template', '=', is_template),"
        " ('type', 'in', ['product', 'consu']), '|',"
        " ('company_id', '=', False), ('company_id', '=', company_id)]",
    )
    is_template = fields.Boolean(string=_("Template"), default=False)

    def action_toggle_is_template(self):
        self.is_template = not self.is_template

    @api.onchange("mrp_routing_ids")
    def _onchange_mrp_routing_ids(self):
        if self.mrp_routing_ids:
            self.operation_ids = [[5, 0]]
            for mrp_routing_id in self.mrp_routing_ids:
                for record in mrp_routing_id.mrp_routing_line_ids:
                    self.operation_ids = [
                        [
                            0,
                            0,
                            {
                                "name": f"<{record.mrp_routing_id.name}> {record.mrp_operation_id.name}",
                                "workcenter_id": record.workcenter_id.id,
                                "time_cycle_manual": record.duration,
                            },
                        ]
                    ]
                for record in mrp_routing_id.mrp_routing_component_ids:
                    find_product = self.bom_line_ids.filtered(
                        lambda x: x.product_id == record.product_id
                    )
                    if find_product:
                        find_product.write({"product_qty": record.product_qty})
                    else:
                        self.bom_line_ids = [
                            [
                                0,
                                0,
                                {
                                    "product_id": record.product_id.id,
                                    "product_qty": record.product_qty,
                                    "product_uom_id": record.product_uom_id.id,
                                },
                            ]
                        ]
