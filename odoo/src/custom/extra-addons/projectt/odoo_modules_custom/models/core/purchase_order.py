from odoo import fields, models, api
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    READONLY_STATES = {
        "purchase": [("readonly", True)],
        "done": [("readonly", True)],
        "cancel": [("readonly", True)],
    }
    partner_id = fields.Many2one(
        "res.partner",
        string="Vendor",
        required=True,
        states=READONLY_STATES,
        change_default=True,
        tracking=True,
        domain="[ '|', ('company_id', '=', company_id), ('company_id', '=', False), ('x_autorised', '=', True) ]",
        help="You can find a vendor by its Name, TIN, Email or Internal Reference.",
    )

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
