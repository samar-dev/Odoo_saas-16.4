{
    "name": "Partner Invoice Limit",
    "version": "saas~16.4.1.0.0",
    "description": "Partner Invoice Limit",
    "summary": "Block customer from buying goods "
    "after reaching a predefined non paid invoices",
    "category": "External",
    "author": "VEGANET",
    "website": "https://www.vegagroup.com.tn",
    "license": "Other proprietary",
    "depends": ["base", "sale"],
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
