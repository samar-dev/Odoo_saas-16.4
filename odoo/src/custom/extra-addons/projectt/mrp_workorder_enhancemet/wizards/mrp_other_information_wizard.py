from odoo import fields, models


class MrpOtherInformationWizard(models.TransientModel):
    _name = "mrp.other.information.wizard"

    operator_employee_ids = fields.Many2many(
        "hr.employee",
        string="employees with access",
        store=True,
        readonly=False,
        domain="[('workcenter_manufacturing', '=', True)]",
    )
    production_planning_reference = fields.Char(string="Production planning reference")
    note = fields.Text(string="Note")
    production_id = fields.Many2one("mrp.production", "Manufacturing Order")

    def button_add_information(self):
        self.env["mrp.production"].search([("id", "=", self.production_id.id)]).write(
            {
                "operator_employee_ids": [(6, 0, self.operator_employee_ids.ids)],
                "production_planning_reference": self.production_planning_reference,
                "note": self.note,
            }
        )
