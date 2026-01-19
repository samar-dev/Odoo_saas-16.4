from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_template_code = fields.Char()
    sequence_id = fields.Many2one(comodel_name="ir.sequence")

    def _search_category_with_sequence(self):
        """
        Search for the first category in the hierarchy
        that has sequence_by_category set to True.
        :return: parent category id where sequence_by_category == True
        """
        current_category = self.categ_id
        if current_category.sequence_by_category:
            return current_category
        parent_category = current_category.parent_id
        while parent_category:
            if parent_category.sequence_by_category:
                return parent_category
            parent_category = parent_category.parent_id

    def _generate_reference(self):
        # Ensure that there is only one record in the current environment
        self.ensure_one()

        # Search for the category with the appropriate sequence
        category_id = self._search_category_with_sequence()

        # Initialize reference variable
        reference = None

        # Check if a category with the required sequence is found
        if category_id:
            # Retrieve the parent path of the category
            category_path = category_id.parent_path

            # Extract category IDs from the path and convert them to integers
            category_ids = map(
                lambda category: int(category), category_path.rstrip("/").split("/")
            )

            # Fetch category prefixes for categories with sequence enabled
            category_prefixes = (
                self.env["product.category"]
                .browse(category_ids or 0)
                .filtered_domain([("sequence_by_category", "=", True)])
                .mapped(lambda category: category.sequence_id.prefix)
            )

        # Check if the category, sequence, and prefixes are available
        if category_id and category_id.sequence_id and category_prefixes:
            # Construct the reference by joining prefixes
            # and padding the sequence number
            reference = "-".join(category_prefixes) + str(
                category_id.sequence_id.number_next_actual
            ).zfill(category_id.sequence_id.padding)

        # Return the generated reference and the category ID
        return reference, category_id

    def _increment_category_sequence(self, category_id):
        category_id.sequence_id.sudo().number_next_actual += 1

    def _set_product_default_code(self, product_template_id):
        sequence = 1
        for product_id in product_template_id.product_variant_ids:
            product_id._generate_product_default_code(sequence)
            sequence += 1

    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        if "categ_id" in vals:
            if self.qty_available > 0 and self.product_template_code:
                pass
            else:
                self.product_template_code, category_id = self._generate_reference()
                if category_id:
                    self.default_code = self.product_template_code
                    self._increment_category_sequence(category_id)
                    self._set_product_default_code(self)
        if "attribute_line_ids" in vals:
            self._set_product_default_code(self)
        return res

    @api.model_create_multi
    def create(self, values):
        res = super(ProductTemplate, self).create(values)
        for product_template_id, value in zip(res, values):
            (
                product_template_id.product_template_code,
                category_id,
            ) = product_template_id._generate_reference()
            if category_id:
                product_template_id.default_code = (
                    product_template_id.product_template_code
                )
                product_template_id._increment_category_sequence(category_id)
                self._set_product_default_code(product_template_id)
        return res

    def action_generate_default_code(self):
        if self.filtered(lambda product: product.qty_available > 0.0 and product.product_template_code):
            raise ValidationError(
                _(
                    "Updating the product reference "
                    "with a quantity of stock > 0 is not possible"
                )
            )
        for record in self:
            if not record.product_template_code and not record.default_code:
                record.product_template_code, category_id = record._generate_reference()
                if category_id:
                    record.default_code = record.product_template_code
                    record._increment_category_sequence(category_id)
                    record._set_product_default_code(record)
            else:
                raise ValidationError(
                    _("The product %s already has a reference", record.name)
                )
