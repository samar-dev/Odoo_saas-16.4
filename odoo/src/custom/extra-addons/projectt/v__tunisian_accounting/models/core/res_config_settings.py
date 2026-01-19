from odoo import _, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_v__payment_methods = fields.Boolean(
        string=_("Méthodes de paiement"),
        default=False,
        config_parameter="v__tunisian_accounting.v__payment_methods",
    )
    module_v__payment_methods_tracking = fields.Boolean(
        string=_("Suivi des méthodes de paiement"),
        default=False,
        config_parameter="v__tunisian_accounting.v__payment_methods_tracking",
    )
    module_v__payment_replace = fields.Boolean(
        string=_("Remplacement de paiement"),
        default=False,
        config_parameter="v__tunisian_accounting.v__payment_replace",
    )
    module_v__tax_stamp = fields.Boolean(
        string=_("Timbre Fiscal"),
        default=False,
        config_parameter="v__tunisian_accounting.v__tax_stamp",
    )
    module_v__withholding_taxes = fields.Boolean(
        string=_("Retenue à la source"),
        default=False,
        config_parameter="v__tunisian_accounting.v__withholding_taxes",
    )
    module_v__payment_methods_print = fields.Boolean(
        string=_("Rapports des méthodes de paiement"),
        default=False,
        config_parameter="v__tunisian_accounting.v__payment_methods_print",
    )
    module_v__account_imputation = fields.Boolean(
        string=_("Imputation des comptes"),
        default=False,
        config_parameter="v__tunisian_accounting.v__account_imputation",
    )
    module_v__automatic_commission_entries = fields.Boolean(
        string=_("Commission Automatique"),
        default=False,
        config_parameter="v__tunisian_accounting.v__automatic_commission_entries",
    )
    module_v__factoring_payments = fields.Boolean(
        string=_("Paiements de factoring"),
        default=False,
        config_parameter="v__tunisian_accounting.v__factoring_payments",
    )
