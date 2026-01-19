from odoo import _, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_method_access_guard = fields.Boolean(
        string=_("Method Access Guard"),
        config_parameter="v__access_guard.method_access_guard",
    )
    module_data_access_guard = fields.Boolean(
        string=_("Data Access Guard"),
        config_parameter="v__access_guard.data_access_guard",
    )
