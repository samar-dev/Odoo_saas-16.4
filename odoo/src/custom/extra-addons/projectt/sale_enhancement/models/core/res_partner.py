from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    x_customer_type = fields.Selection(
        [
            ("local", "Local customer"),
            ("export", "Export customer"),
            ("import_supplier", "Import supplier"),
            ("local_supplier", "Local supplier"),
            ("prospect_client", "Prospect client"),
            ("prospect_fournisseur", "Prospect fournisseur"),
        ],
        string="Type",
    )

    x_invoice_policy = fields.Selection(
        [("order", "Quantités commandées"), ("delivery", "Quantités livrées")],
        string="Politique de facturation",
        help="Quantité commandée : Facturer les quantités commandées par le client.\n"
        "Quantité livrée : Facturer les quantités livrées au client.",
    )
