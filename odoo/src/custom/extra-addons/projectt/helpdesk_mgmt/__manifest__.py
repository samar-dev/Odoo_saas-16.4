# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Helpdesk Management",
    "summary": """
        Helpdesk""",
    "version": "saas~16.4.0.0.1",
    "license": "AGPL-3",
    "category": "After-Sales",
    "author": "AdaptiveCity, "
              "Tecnativa, "
              "ForgeFlow, "
              "C2i Change 2 Improve, "
              "Domatix, "
              "Factor Libre, "
              "SDi Soluciones, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/helpdesk",
    "depends": ["mail", "portal", "helpdesk","maintenance"],
    "data": [
        "data/sequences.xml",
        "views/helpdesk_ticket_team_views.xml",
        "views/helpdesk_alias_member_views.xml",
        "views/helpdesk_ticket_views.xml",
        "security/ir.model.access.csv",
    ],

    "development_status": "Beta",
    "application": True,
    "installable": True,
}
