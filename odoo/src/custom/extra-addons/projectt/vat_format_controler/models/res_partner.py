import re
from odoo import models, api, exceptions


def _check_vat_format(vat, is_company):
    if not vat:
        return "Le N° TVA/CIN est vide"

    if is_company:
        # VAT number format for companies
        if not re.match(r"^[0-9]{7}[A-Z]{3}[0-9]{3}$", vat):
            return "Le N° TVA ne respecte pas le format approprié. Exemple: 1234567ABC000"
    else:
        # VAT number format for individuals or non-companies
        if not re.match(r"^[0-9]{8}$", vat):
            return "Le N° TVA ne respecte pas le format approprié. Exemple: 04251241"

    return ""


class Partner(models.Model):
    _inherit = "res.partner"

    @api.onchange("x_customer_type", "vat", "buyer_id", "property_account_payable_id", "property_account_receivable_id")
    def _check_vat(self):
        for record in self:
            # Check if the VAT number should be validated based on customer type
            if record.x_customer_type in ["local", "local_supplier"]:
                validation_message = _check_vat_format(record.vat, record.is_company)
                if validation_message:
                    raise exceptions.ValidationError(validation_message)
