from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    workcenter_manufacturing = fields.Boolean(string="Work center manufacturing")

    def get_all_employees(self, login=False):
        if login:
            self.login_user_employee()
        all_employees = self.search_read(
            [("workcenter_manufacturing", "=", True)], fields=["id", "name"]
        )
        all_employees_ids = {employee["id"] for employee in all_employees}
        employees_connected = list(
            filter(
                lambda employee_id: employee_id in all_employees_ids,
                self.get_employees_connected(),
            )
        )
        out = {
            "admin": self.get_session_owner(),
            "connected": self.get_employees_wo_by_employees(employees_connected),
        }
        if login:
            out["all"] = all_employees
        return out
