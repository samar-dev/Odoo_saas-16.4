{
    "name": "Block Unpaid Customers",
    "version": "saas~16.4.1.3.1",
    "description": "Block Unpaid Customers",
    "summary": "Block customers manually or"
    " automatically if they have payments not paid",
    "category": "External",
    "author": "VEGANET",
    "website": "https://www.vegagroup.com.tn",
    "license": "Other proprietary",
    "depends": ["base", "sale", "stock"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "security/record_rules.xml",
        "views/core/res_config_settings.xml",
        "views/core/res_partner.xml",
        "views/core/sale_order.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
    "sequence": 1,
}
