from odoo import _, fields, models


class MrpRoutingWorkcenter(models.Model):
    _inherit = "mrp.routing.workcenter"

    is_template = fields.Boolean(string=_("Template"), default=False)
    bom_id = fields.Many2one(required=False)
    company_id = fields.Many2one(default=lambda self: self.env.company, related=False)

    def action_toggle_is_template(self):
        self.is_template = not self.is_template
