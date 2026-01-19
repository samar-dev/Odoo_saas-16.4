{
    "name": "Stock Credit Note",
    "version": "saas~16.4.1.0.2",
    "description": "Stock Credit Note",
    "category": "External",
    "author": "VegaNET",
    "website": "https://vegagroup.com.tn",
    "license": "Other proprietary",
    "depends": ["base", "stock", "account", "sale_stock", "stock_picking_batch"],
    "data": [
        "views/stock_picking_views.xml",
        "views/stock_picking_type_views.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
    "sequence": 1,
}
