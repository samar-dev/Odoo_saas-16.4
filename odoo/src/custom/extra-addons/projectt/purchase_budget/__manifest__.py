# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Purchase Budget Management",
    "category": "Accounting/Accounting",
    "description": """
Use budgets to compare actual with expected revenues and costs
--------------------------------------------------------------
""",
    "depends": ["account", "base", "mail", "purchase"],
    "data": [
        "security/ir.model.access.csv",
        # "security/account_budget_security.xml",
        "views/account_budget_views.xml",
        "views/product_template_views.xml",
        "report/budget_template.xml",
        # "views/account_analytic_account_views.xml",
    ],
    "demo": [""],
    "license": "OEEL-1",
}
