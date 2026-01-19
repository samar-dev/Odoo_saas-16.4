{
    "name": "Partner Validation",
    "version": "saas~16.4.1.0.2",
    "description": "This module supports a contact validation process",
    "category": "External",
    "author": "VEGANET",
    "website": "https://vegagroup.com.tn",
    "license": "Other proprietary",
    "depends": ["base", "account", "sale", "purchase", "v__message_service"],
    "data": [
        "security/ir.model.access.csv",
        "views/core/res_partner_views.xml",
        "views/res_partner_validator_list_views.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
    "sequence": 1,
}
