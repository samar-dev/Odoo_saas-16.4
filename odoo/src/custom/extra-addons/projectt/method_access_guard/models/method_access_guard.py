from odoo import api, fields, models, _


class MethodAccessGuard(models.Model):
    _name = "method.access.guard"
    _description = _("Method Access Guard")
    _rec_name = "method_name"
    _order = "id desc"

    method_name = fields.Char(
        string=_("Method name"),
        required=True,
        help=_("The method name you would like to prevent the user from executing it."),
    )
    model_id = fields.Many2one(
        string=_("Model"),
        comodel_name="ir.model",
        required=True,
        ondelete="cascade",
    )
    model_name = fields.Char(related="model_id.model")
    group_ids = fields.Many2many(
        string=_("Groups"),
        comodel_name="res.groups",
        help=_(
            "Add the groups you would like to prevent them"
            " from executing certain methods."
        ),
    )
    type = fields.Selection(
        string=_("Type"),
        selection=[("blacklist", _("Blacklist")), ("whitelist", _("Whitelist"))],
        required=True,
        default="blacklist",
    )
    user_ids = fields.Many2many(
        string=_("Users"),
        comodel_name="res.users",
        help=_(
            "Add the users you would like to prevent them"
            " from executing certain methods."
        ),
    )
    blacklisted_user_ids = fields.Many2many(
        comodel_name="res.users", compute="_compute_blacklisted_user_ids"
    )
    whitelisted_user_ids = fields.Many2many(
        comodel_name="res.users", compute="_compute_whitelisted_user_ids"
    )
    message = fields.Char(string=_("Message"), required=True, translate=True)

    @api.depends("group_ids", "user_ids", "type")
    def _compute_blacklisted_user_ids(self):
        for record in self:
            record.whitelisted_user_ids = None
            record.blacklisted_user_ids = (
                record.group_ids.mapped("users") + record.user_ids
            )

    @api.depends("group_ids", "user_ids", "type")
    def _compute_whitelisted_user_ids(self):
        for record in self:
            record.blacklisted_user_ids = None
            record.whitelisted_user_ids = (
                record.group_ids.mapped("users") + record.user_ids
            )
