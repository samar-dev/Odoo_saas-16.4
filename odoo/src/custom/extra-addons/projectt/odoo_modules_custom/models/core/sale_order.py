from datetime import date

from odoo import fields, models, api
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange("currency_id")
    def check_rate_date(self):
        for record in self:
            value = record.currency_id
            print(value)
            # Assuming currency_id is an instance of the currency model
            if (
                value and value.name != "TND" and record.company_id.have_currency
            ):  # Check currency code
                future_rates = value.rate_ids.filtered(lambda r: r.name >= date.today())
                print(len(future_rates))
                if not future_rates:
                    raise UserError(
                        f"Aucun taux futur trouvé pour la devise {value.name} le {date.today()}."
                    )
                elif len(future_rates) > 1:
                    raise UserError(
                        f"Tu ne peux pas fixer une devise à une date ultérieure à  {date.today()}."
                    )
