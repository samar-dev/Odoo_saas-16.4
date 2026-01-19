from odoo import models, fields, _


class ManufacturingOrder(models.Model):
    _inherit = "mrp.production"

    operator_employee_ids = fields.Many2many(
        "hr.employee",
        string="employees with access",
        store=True,
        readonly=False,
        domain="[('workcenter_manufacturing', '=', True)]",
    )
    production_planning_reference = fields.Char(string="Production planning reference")
    note = fields.Text(string="Note")

    def button_add_information(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "mrp.other.information.wizard",
            "views": [
                [
                    self.env.ref(
                        "mrp_workorder_enhancemet.view_mrp_other_information_wizard_form"
                    ).id,
                    "form",
                ]
            ],
            "name": _("Add other information"),
            "target": "new",
            "context": {
                "default_production_id": self.id,
            },
        }
