from odoo import models


class AccountTax(models.Model):
    _inherit = "account.tax"

    def _convert_to_tax_base_line_dict(
        self,
        base_line,
        partner=None,
        currency=None,
        product=None,
        taxes=None,
        price_unit=None,
        quantity=None,
        discount=None,
        account=None,
        analytic_distribution=None,
        price_subtotal=None,
        is_refund=False,
        rate=None,
        handle_price_include=True,
        extra_context=None,
    ):
        return super(AccountTax, self)._convert_to_tax_base_line_dict(
            base_line,
            partner,
            currency,
            product,
            taxes,
            price_unit,
            quantity,
            discount=discount or self._context.get("discount"),
            account=account,
            analytic_distribution=analytic_distribution,
            price_subtotal=price_subtotal,
            is_refund=is_refund,
            rate=rate,
            handle_price_include=handle_price_include,
            extra_context=extra_context,
        )
