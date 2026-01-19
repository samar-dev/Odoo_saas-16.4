from odoo import api, exceptions, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_tax_stamp = fields.Boolean(
        string="Timbre Fiscal", default=False, copy=False, tracking=True
    )

    @api.model_create_multi
    def create(self, vals_list):
        for value in vals_list:
            if value.get("is_tax_stamp") and self.search_count(
                [("is_tax_stamp", "=", True), ("company_id", "=", self.env.company.id)]
            ):
                raise exceptions.ValidationError(
                    "Un produit de timbre fiscal existe déjà dans votre système"
                )
        res = super(ProductTemplate, self).create(vals_list)
        return res

    def write(self, vals):
        if vals.get("is_tax_stamp") and self.search_count(
            [("is_tax_stamp", "=", True), ("company_id", "=", self.env.company.id)]
        ):
            raise exceptions.ValidationError(
                "Un produit de timbre fiscal existe déjà dans votre système"
            )
        res = super(ProductTemplate, self).write(vals)
        return res
