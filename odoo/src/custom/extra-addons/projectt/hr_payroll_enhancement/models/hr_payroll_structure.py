from odoo import models, fields


class HrPayslip(models.Model):
    _inherit = "hr.payroll.structure"

    contract_type = fields.Selection(
        [
            ("stc", "STC"),
            ("ind", "INDEPENDANT"),
            ("other", "Other"),
        ],
        string="Type",
        default="other",
        help="Type selection: stc or other",
    )



