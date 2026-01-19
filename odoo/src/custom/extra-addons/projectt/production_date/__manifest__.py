{
    "name": "Production Date",
    "version": "saas~16.4.1.0.1",
    "description": "Production Date",
    "category": "External",
    "author": "VEGANET",
    "website": "https://vegagroup.com.tn",
    "license": "Other proprietary",
    "depends": ["base", "stock", "product_expiry"],
    "data": [
        "views/res_config_settings_views.xml",
        "views/product_template_views.xml",
        "views/production_lot_view.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
    "sequence": 1,
}
