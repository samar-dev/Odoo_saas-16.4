# -*- coding: utf-8 -*-

{
    "name": "Purchase Discount",
    "summary": "Purchase Discount",
    "description": """
    This module allows to add the discount per line in the purchase orders
    """,
    "version": "saas~16.4.1.1.0",
    "category": "External",
    "author": "VegaNET",
    "website": "https://vegagroup.com.tn",
    "license": "Other proprietary",
    "depends": [
        "base",
        "purchase",
        "sale",
        "account",
        "sale_purchase_inter_company_rules",
    ],
    "data": [
        "views/purchase_views.xml",
    ],
    "demo": [],
    "installable": True,
    "application": True,
}
