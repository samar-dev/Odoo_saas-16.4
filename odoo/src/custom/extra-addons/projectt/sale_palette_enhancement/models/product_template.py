from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_pallet = fields.Boolean(string="Est une palette", default=False)
    department_id = fields.Many2one('hr.department', default=lambda self: self.env.user.employee_ids.department_id,
                                    string="Department", tracking=3)