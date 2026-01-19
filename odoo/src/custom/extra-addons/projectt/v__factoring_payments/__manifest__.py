{
    "name": "Factoring Payments",
    "version": "saas~16.4.2.0.0",
    "description": "Factoring Payments",
    "summary": "Factoring allows the business to get immediate cash "
    "instead of waiting for customers to pay their invoices",
    "category": "External",
    "author": "VEGANET",
    "website": "https://www.vegagroup.com.tn",
    "license": "Other proprietary",
    "depends": ["base", "account", "v__tunisian_accounting", "v__payment_methods"],
    "data": [
        "security/ir.model.access.csv",
        "security/record_rules.xml",
        "data/ir_sequence.xml",
        "views/account_factoring.xml",
        "views/core/account_journal.xml",
        "views/core/account_payment.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
    "sequence": 1,
}
