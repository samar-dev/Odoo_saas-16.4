# -*- coding: utf-8 -*-
{
    "name": "RH CUSTOM MODULES",
    "summary": """
        RH CUSTOM MODULES
        """,
    "description": """
    Module pour le Système d'information RH
    """,
    "author": "Odoo",
    "website": "",
    "category": "hr",
    "version": "saas~16.4.1.0.2",
    "depends": [
        "base",
        "hr",
        "v__message_service",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/core/hr_employee.xml",
        "views/core/hr_contract.xml",
        "views/hr_convention.xml",
        "data/email_template.xml",
        "data/service_cron.xml",
    ],
    "images": ["static/description/odoo_icon.png"],
    "license": "Other proprietary",
    "installable": True,
    "application": True,
    "auto_install": False,
}
