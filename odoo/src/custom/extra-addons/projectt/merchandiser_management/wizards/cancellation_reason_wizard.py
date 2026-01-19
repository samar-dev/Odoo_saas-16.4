from odoo import fields, models


class CancellationReasonWizard(models.TransientModel):
    _name = "cancellation.reason.wizard"

    reason = fields.Text(string="Reason")

    def add_cancellation_reason(self):
        active_ids = self.env.context.get("active_ids")
        for planning in self.env["merchandise.planning"].browse(active_ids):
            planning.reason = self.reason
            planning.state = "cancelled"
