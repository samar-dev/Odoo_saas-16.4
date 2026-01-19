from odoo import models, fields


class HrSalaryRule(models.Model):
    _inherit = "hr.salary.rule"

    rule_type = fields.Selection(
        [
            ("hours", "Hours"),
            ("money", "Money"),
        ],
        string="Rule Type",
        default="money",
    )
