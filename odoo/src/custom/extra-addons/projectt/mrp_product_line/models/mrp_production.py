from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    product_id = fields.Many2one(
        comodel_name="product.product",
        domain="""['&', ('is_template', '=', False),
        ('type', 'in', ['product', 'consu']),
        '|',
        ('company_id', '=', False),
        ('company_id', '=', company_id)
        ]
        """,
    )

    bom_id = fields.Many2one(
        domain="""[
        '&', ('is_template', '=', False),
        '&',
        '|',
        ('company_id', '=', False),
        ('company_id', '=', company_id),
        '&',
        '|',
        ('product_id','=',product_id),
        '&',
        ('product_tmpl_id.product_variant_ids','=',product_id),
        ('product_id','=',False),
        ('type', '=', 'normal')]""",
    )
