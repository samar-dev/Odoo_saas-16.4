from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _generate_product_default_code(self, sequence):
        if (
            self.product_template_attribute_value_ids
            and self.product_tmpl_id.product_template_code
        ):
            if self.product_tmpl_id.product_variant_count > 1:
                self.default_code = (
                    self.product_tmpl_id.product_template_code + "-" + str(sequence)
                )
            else:
                self.default_code = self.product_tmpl_id.product_template_code
