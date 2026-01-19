# Copyright 2013 Guewen Baconnier, Camptocamp SA
# Copyright 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models, api


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    cancel_reason_id = fields.Many2one(
        comodel_name="purchase.order.cancel.reason",
        string="Reason for cancellation",
        ondelete="restrict",

    )

    is_forced_closed = fields.Boolean(
        string="Forced Closed",
    )

    cancel_reason_description = fields.Text(
        string="Cancellation Description",
        related="cancel_reason_id.description",
        readonly=True,
    )

    def reset_cancel_uegent(self):
        """Undo forced closure and remove cancel reason."""
        self.write({
            "is_forced_closed": False,
            "cancel_reason_id": False,
            "invoice_status": 'to invoice',
        })
