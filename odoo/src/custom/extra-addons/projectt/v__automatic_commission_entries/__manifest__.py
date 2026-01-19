{
    "name": "Automatic Commission Entries",
    "version": "saas~16.4.1.0.1",
    "description": "Automatic Commission Entries",
    "summary": "Add the pposibility to create journal entries"
    " for commission automatically",
    "category": "External",
    "author": "VEGANET",
    "website": "https://www.vegagroup.com.tn",
    "license": "Other proprietary",
    "depends": ["base", "v__tunisian_accounting", "v__payment_methods_tracking"],
    "data": [
        "security/ir.model.access.csv",
        "views/account_commission.xml",
        "views/payment_method_line_stage.xml",
        "views/core/account_payment.xml",
        "wizards/next_stage_payment_wiz.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
    "sequence": 1,
}
