from odoo import api, fields, models
from odoo.exceptions import ValidationError


class NextStagePaymentWiz(models.TransientModel):
    _name = "next.stage.payment.wiz"

    date = fields.Date(
        string="Date", required=True, default=lambda self: fields.Date.today()
    )

    @api.constrains("date")
    def _check_date(self):
        if self.date > fields.Date.today():
            raise ValidationError(
                "La date doit être inférieure ou égale à la date du jour"
            )

    def button_call_next_stage(self):
        active_ids = self._context.get("active_ids")
        payment_ids = self.env["account.payment"].browse(active_ids)
        callback = getattr(
            payment_ids.with_context(entry_date=self.date, do_not_call_wizard=True),
            self._context.get("callback"),
        )
        callback()
