from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    x_type = fields.Selection(
        string="Autre Type",
        selection=[("chest", "Coffre"), ("to_be_cashed", "À encaissé")],
        tracking=True,
    )

    def _get_available_payment_method_lines(self, payment_type):
        res = super(AccountJournal, self)._get_available_payment_method_lines(
            payment_type
        )
        if payment_type == "inbound" and self.x_type != "chest":
            res = res.filtered(lambda item: item.code not in ("v-check", "v-banknote"))
        return res
