from odoo import fields, models, _
from odoo.exceptions import ValidationError


class Validator(models.Model):
    _name = "res.partner.validator"
    _description = "Partner Validator"
    _rec_name = "validator_id"

    validator_id = fields.Many2one(comodel_name="res.users", string=_("Validator"))
    state = fields.Selection(
        string=_("State"),
        selection=[
            ("waiting", _("Waiting")),
            ("refused", _("Refused")),
            ("approved", _("Validated")),
        ],
        default="waiting",
        readonly=True,
    )

    partner_id = fields.Many2one(
        comodel_name="res.partner", string=_("Partner"), required=True
    )
    notification_sent = fields.Boolean(string="Notification Sent", default=False)

    def unlink(self):
        if self.state == "refused" or self.state == "approved":
            raise ValidationError(_("A validated or refused request cannot be deleted"))
        return super().unlink()


class ResPartnerValidatorList(models.Model):
    _name = "res.partner.validator.list"
    _description = "Partner Validator Template"

    name = fields.Char(string="Name", required=True)
    validator_ids = fields.Many2many(
        comodel_name="res.users",
        relation="partner_validator_list_users_rel",
        column1="list_id",
        column2="user_id",
        string="Validators",
        required=True,
    )
