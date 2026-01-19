from odoo import fields, models, api
from odoo.exceptions import UserError


class PlanningSlot(models.Model):
    _inherit = "planning.slot"

    assortment_id = fields.Many2one("assortment", string="Assortment")
    store_id = fields.Many2one("res.partner.store", string="Store")
    merchandise_planning_id = fields.Many2one(
        "merchandise.planning", string="Merchandise Planning"
    )
    partner_id = fields.Many2one("res.partner", string="Partner")
    merchandise_state = fields.Selection(
        related="merchandise_planning_id.state", string="Merchandise state"
    )

    def button_create_merchandise(self):
        for record in self:
            if record.assortment_id:
                # Ensure partner_id is set
                partner_id = record.partner_id.id or (
                    record.partner_id.id if record.partner_id else False
                )
                if not partner_id:
                    raise UserError(
                        "Partner must be set before creating Merchandise Planning."
                    )

                merchandise = self.env["merchandise.planning"].create(
                    {
                        "planning_id": record.id,
                        "partner_id": partner_id,
                        "state": "draft",
                        "assortment_id": record.assortment_id.id,
                    }
                )
                record.merchandise_planning_id = merchandise.id

    @api.onchange("assortment_id")
    def _onchange_assortment_partner(self):
        for record in self:
            if record.assortment_id:
                # automatically fill partner_id from assortment_partner_id
                record.partner_id = record.assortment_id.partner_id.id
