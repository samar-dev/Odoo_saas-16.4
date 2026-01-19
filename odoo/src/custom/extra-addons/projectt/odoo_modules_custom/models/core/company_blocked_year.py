from odoo import models, fields

class CompanyBlockedYear(models.Model):
    _name = "res.company.blocked.year"
    _description = "Blocked Accounting Year"
    _order = "year desc"

    year = fields.Integer(
        string="Year",
    )

    name = fields.Char('Name', required=True,)

    company_id = fields.Many2one(
        "res.company",
        required=True,
        ondelete="cascade"
    )

    _sql_constraints = [
        (
            "company_year_unique",
            "unique(company_id, year)",
            "This year is already blocked for this company."
        )
    ]
