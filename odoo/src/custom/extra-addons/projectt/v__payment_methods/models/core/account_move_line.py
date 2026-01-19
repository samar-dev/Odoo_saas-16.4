from odoo import api, models
from odoo.exceptions import ValidationError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model_create_multi
    def create(self, vals_list):
        res = super(AccountMoveLine, self).create(vals_list)
        for line in res:
            if line.account_id.is_partner_mandatory and not line.partner_id:
                raise ValidationError(
                    f"Prière de spécifier le partenaire pour l'écriture sur le compte "
                    f"{line.account_id.display_name}"
                )
        return res

    @api.model
    def _get_default_line_name(self, document, amount, currency, date, partner=None):
        res = super(AccountMoveLine, self)._get_default_line_name(
            document, amount, currency, date, partner
        )
        # a little hack to keep using the original method as well
        # this happens if the payment method is not one of our custom payment methods
        if isinstance(document, tuple):
            return document[0]
        return res
