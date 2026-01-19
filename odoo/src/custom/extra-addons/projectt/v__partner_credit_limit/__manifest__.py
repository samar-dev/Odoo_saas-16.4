{
    "name": "Partner Credit Limit",
    "version": "saas~16.4.1.2.0",
    "description": "Partner Credit Limit",
    "summary": "Block customer from buying goods "
    "after reaching a predefined credit amount",
    "category": "External",
    "author": "VEGANET",
    "website": "https://www.vegagroup.com.tn",
    "license": "Other proprietary",
    "depends": ["base", "sale", "v__payment_replace"],
    "data": [
        "security/security.xml",
        "views/core/res_config_settings.xml",
        "views/core/res_partner.xml",
        "views/core/sale_order.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
    "sequence": 1,
}
