from odoo import api, exceptions, fields, models, _


class MrpRouting(models.Model):
    _name = "mrp.routing"
    _description = "Product Line"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string=_("Production Phase"), required=True, tracking=True)
    number = fields.Char(
        string=_("Reference"), required=True, readonly=True, default="/"
    )
    state = fields.Selection(
        string=_("State"),
        selection=[
            ("draft", _("Draft")),
            ("under_approval", _("Under Approval")),
            ("approved", _("Approved")),
            ("declined", _("Declined")),
        ],
        required=True,
        default="draft",
        tracking=True,
    )
    product_family_ids = fields.Many2many(
        string=_("Product Family"), comodel_name="product.category", tracking=True
    )
    raw_material_family_id = fields.Many2one(
        string=_("Raw Material Family"), comodel_name="product.category", tracking=True
    )
    model = fields.Char(string=_("Model"), tracking=True)
    partner_id = fields.Many2one(
        string=_("Customer"), comodel_name="res.partner", tracking=True
    )
    season = fields.Char(string=_("Season"), tracking=True)
    version = fields.Char(string=_("Version"), required=True, tracking=True)
    size = fields.Integer(string=_("Size(s)"), required=True, tracking=True)
    model_time = fields.Float(
        string=_("Model time"), compute="_compute_model_time", store=True, tracking=True
    )

    mrp_routing_line_ids = fields.One2many(
        string=_("Operations"),
        comodel_name="mrp.routing.line",
        inverse_name="mrp_routing_id",
    )

    mrp_routing_component_ids = fields.One2many(
        string=_("Components"),
        comodel_name="mrp.routing.component",
        inverse_name="mrp_routing_id",
    )
    attribute_line_ids = fields.Many2many(
        comodel_name="product.attribute.value", string=_("Product labels")
    )

    @api.depends("mrp_routing_line_ids", "mrp_routing_line_ids.duration")
    def _compute_model_time(self):
        for record in self:
            record.model_time = sum(record.mrp_routing_line_ids.mapped("duration"))

    def action_set_approved(self):
        admin_group = self.env.ref("mrp.group_mrp_manager")
        user_ids = admin_group.users
        self.state = "approved"
        if user_ids:
            channel_name = "Approbation des gammes"
            message = "<p>Votre demande: "
            message += f'<a href="#" data-oe-model="{self._name}" data-oe-id'
            message += f'="{self.id}">{self.name}</a><br/>'
            message += "a été validée par le service qualité, "
            message += "vous pouvez l'utiliser dès maintenant dans le module BOMs</p>"
            self._base_send_a_message(user_ids, channel_name, message)
            return self._base_display_notification(
                title=channel_name,
                type="success",
                message="Votre demande a été envoyée avec succès",
                sticky=False,
            )
        else:
            return self._base_display_notification(
                type="warning",
                message="Impossible de trouver un administrateur de fabrication",
                sticky=False,
            )

    def action_set_declined(self):
        self.state = "declined"

    def action_send_to_approve(self):
        if not self.mrp_routing_line_ids:
            raise exceptions.ValidationError(
                _("You must have at least one operation in order to send the request")
            )
        admin_group = self.env.ref("quality.group_quality_manager")
        user_ids = admin_group.users
        if user_ids:
            channel_name = "Demande d'approbation"
            message = "<p>Une nouvelle gamme de produits a été créée"
            message += " et en attente d'approbation: "
            message += f'<a href="#" data-oe-model="{self._name}" data-oe-id'
            message += f'="{self.id}">{self.name}</a></p>'
            self._base_send_a_message(user_ids, channel_name, message)
            self.state = "under_approval"
            return self._base_display_notification(
                title=channel_name,
                type="success",
                message="Votre demande a été envoyée avec succès",
                sticky=False,
            )
        else:
            return self._base_display_notification(
                title="Qualification des fournisseurs",
                type="warning",
                message="Impossible de trouver un administrateur de qualité",
                sticky=False,
            )

    @api.model_create_multi
    def create(self, vals_list):
        res = super(MrpRouting, self).create(vals_list)
        for record in res:
            record.number = self.env["ir.sequence"].next_by_code(
                "mrp_routing_enhancement.mrp_routing_seq"
            )
        return res

    def unlink(self):
        for record in self:
            if record.state != "draft":
                raise exceptions.ValidationError(
                    _("Only draft document can be deleted")
                )
        return super(MrpRouting, self).unlink()

    def button_reset_to_draft(self):
        self.state = "draft"


class MrpRoutingLine(models.Model):
    _name = "mrp.routing.line"
    _description = "Product Line Operation"

    mrp_routing_id = fields.Many2one(
        string=_("Product Line"), comodel_name="mrp.routing"
    )
    mrp_operation_id = fields.Many2one(
        string=_("Operation"), comodel_name="mrp.routing.workcenter", required=True
    )
    workcenter_id = fields.Many2one(
        string=_("Workcenter"),
        comodel_name="mrp.workcenter",
        related="mrp_operation_id.workcenter_id",
        store=True,
    )
    duration = fields.Float(
        string=_("Duration"), related="mrp_operation_id.time_cycle_manual", store=True
    )
