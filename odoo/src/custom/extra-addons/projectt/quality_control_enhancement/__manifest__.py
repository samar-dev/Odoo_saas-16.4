{
    "name": "Quality enhancement",
    "version": "saas~16.4.1.1.0",
    "description": "add some functionality to the quality module",
    "category": "External",
    "author": "VEGANET",
    "website": "https://vegagroup.com.tn",
    "license": "Other proprietary",
    "depends": ["base", 'quality_control', 'stock', 'mrp'],
    "data": [
        "data/sequences.xml",
        'security/ir.model.access.csv',
        "views/core/quality_views.xml",
        "views/checklist_views.xml",

    ],
    'assets': {
        'web.assets_backend': [
            'quality_control_enhancement/static/src/css/custom_styles.css',
        ],
    },
    "application": False,
    "auto_install": False,
    "installable": True,
    "sequence": 1,
}
