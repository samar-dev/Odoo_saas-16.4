from odoo import _, fields, models
from odoo.tools import safe_eval


class DataAccessGuard(models.Model):
    _name = "data.access.guard"
    _description = _("Data Access Guard")
    _order = "id desc"

    model_id = fields.Many2one(
        string=_("Model"),
        comodel_name="ir.model",
        required=True,
        ondelete="cascade",
    )
    filter_domain = fields.Char(string=_("Domain"), required=True)
    model_name = fields.Char(related="model_id.model")
    group_ids = fields.Many2many(
        string=_("Groups"),
        comodel_name="res.groups",
        help=_("Add groups here, to apply the domain for them"),
    )
    user_ids = fields.Many2many(
        string=_("Users"),
        comodel_name="res.users",
        help=_("Add users here, to apply the domain for them"),
    )

    def _get_raw_domain(self):
        self.ensure_one()
        return safe_eval.safe_eval(
            self.filter_domain,
            {"user": self.env.user, "env": self.env},
            locals_builtins=True,
        )
