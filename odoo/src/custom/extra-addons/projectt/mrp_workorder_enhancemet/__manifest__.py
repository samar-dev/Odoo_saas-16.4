{
    "name": "MRP Work Order Enhancement",
    "version": "saas~16.4.1.0.0",
    "description": "MRP Work Order Enhancement",
    "category": "External",
    "author": "VEGANET",
    "website": "https://vegagroup.com.tn",
    "license": "Other proprietary",
    "depends": ["base", "mrp_workorder", "hr"],
    "data": [
        "security/ir.model.access.csv",
        "views/hr_employee_views.xml",
        "views/mrp_production_views.xml",
        "wizards/mrp_other_information_wizard_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "mrp_workorder_enhancemet/static/src/**/*.xml",
        ],
    },
    "application": False,
    "auto_install": False,
    "installable": True,
    "sequence": 1,
}
