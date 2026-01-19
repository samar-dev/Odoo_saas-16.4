{
    "name": "Account reconciliation",
    "description": "Account payments reconciliation",
    "version": "saas~16.4.1.0.2",
    "author": "Freelancer",
    "license": "Other proprietary",
    "depends": ["base", "account"],
    "data": [
        "views/account_move_views.xml",
        "wizard/reconciliation_account_wizard_view.xml",
        "security/ir.model.access.csv",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}
