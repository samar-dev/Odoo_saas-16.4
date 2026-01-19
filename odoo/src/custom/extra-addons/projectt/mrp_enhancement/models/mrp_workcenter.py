from odoo import fields, models


class MrpWorkcenter(models.Model):
    _inherit = "mrp.workcenter"

    workcenter_id = fields.Many2one(
        "mrp.workcenter",
        "Parent Work Center",
        index=True,
        ondelete="cascade",
        check_company=True,
        help="The parent work center that includes this work center",
    )
