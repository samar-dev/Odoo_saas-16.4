{
    "name": "odoo landed cost",
    "description": "Customizations added to landed cost",
    "version": "saas~16.4.0.0.1",
    "author": "Freelancer",
    "license": "Other proprietary",
    "depends": [
        "base",
        "account",
        "sale",
        "purchase",
        "stock_landed_costs",
        "stock_account",
    ],
    "data": [
        "views/stock_landed_cost.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}
