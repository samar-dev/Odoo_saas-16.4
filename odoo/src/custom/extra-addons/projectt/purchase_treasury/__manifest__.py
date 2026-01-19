{
    "name": "Purchase Treasury",
    "version": "saas~16.4.1.1.0",
    "depends": ["base", "mail", "account"],
    "author": "Your Name",
    "category": "Accounting",
    "summary": "Manage purchase treasury disbursements by category and month",
    "data": [
        "security/ir.model.access.csv",
        "views/menus.xml",
        "views/treasury_views.xml",
        "views/sector_views.xml",
        "views/treasury_template_views.xml",
        "views/treasury_summary_views.xml",
    ],
    "installable": True,
    "application": True,
}
