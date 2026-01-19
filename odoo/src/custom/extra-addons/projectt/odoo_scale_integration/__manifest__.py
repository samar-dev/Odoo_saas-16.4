{
    "name": "Scale Integration",
    "version": "saas~16.4.1.0.3",
    "category": "Tools",
    "summary": "Integrate Bilanciai D80 Scale with Odoo",
    "depends": ["base", "mail", "stock", "stock_account", "product", "account", "web"],
    "data": [
        "security/ir.model.access.csv",  # Security access control
        "views/scale_view.xml",  # View definitions
        "views/stock_location_views.xml",
        "views/stock_lot_view.xml",
        "views/scale_account_move_line_view.xml",
        "data/sequences.xml",
        "data/cron.xml",
        "report/good_weighing_template.xml",
        "report/invoice_scale_template.xml",
        "report/account_move_scale_template.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "odoo_scale_integration/static/src/js/many2many_tags_field.js",
        ],
    },
    "installable": True,
    "application": False,
}
