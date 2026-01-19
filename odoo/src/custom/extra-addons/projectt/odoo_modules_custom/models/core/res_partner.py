from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.http import request


class ResPartner(models.Model):
    _inherit = "res.partner"

    x_autorised = fields.Boolean(string="Active", default=True)

    @api.model_create_multi
    def create(self, vals_list):
        res = super(ResPartner, self).create(vals_list)
        for record in res:
            if not record.property_account_position_id and record.x_customer_type in [
                "export",
                "import_supplier",
            ]:
                raise ValidationError(
                    _(
                        "La position fiscale est obligatoire si votre client est étranger."
                    )
                )
        return res

    @api.onchange("property_product_pricelist", "x_customer_type")
    def check_partner_postion(self):
        for record in self:
            if not record.property_account_position_id and record.x_customer_type in [
                "export",
                "import_supplier",
            ]:
                raise ValidationError(
                    _(
                        "La position fiscale est obligatoire si votre client est étranger."
                    )
                )

    @api.constrains("vat")
    def _check_vat_exist(self):
        for record in self:
            # Only apply the constraint for specific customer types
            if record.x_customer_type not in ["local", "local_supplier"]:
                continue

            # Check for duplicate VAT among authorized partners
            sol = self.env["res.partner"].search(
                [
                    ("vat", "=", record.vat),
                    ("x_autorised", "=", True),
                    ("id", "!=", record.id),
                ]
            )
            if sol and not record.parent_id:
                raise ValidationError(_("Ce numéro de TVA a déjà été enregistré."))
