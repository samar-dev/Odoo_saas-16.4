from odoo import models, fields, api, _


class Picking(models.Model):
    _inherit = "stock.picking"

    credit_note_id = fields.Many2one(
        comodel_name="account.move",
        string=_("Credit note"),
        compute="_compute_credit_note_id",
        store=True,
    )
    show_reverse_button = fields.Boolean(
        string=_("Show reverse button"),
        default=False,
        compute="_compute_show_reverse_button",
    )

    # -------------------------------------------------------------------------
    # BUSINESS METHODS
    # -------------------------------------------------------------------------
    def _search_invoice(self):
        line_id = self.move_ids_without_package.sale_line_id
        move_id = line_id.sudo().invoice_lines.move_id.filtered(
            lambda move: move.move_type != "out_refund" and move.state == "posted"
        )
        return move_id

    # -------------------------------------------------------------------------
    # COMPUTE METHODS
    # -------------------------------------------------------------------------
    @api.depends("move_ids_without_package.sale_line_id.invoice_lines")
    def _compute_credit_note_id(self):
        for picking in self.filtered(lambda picking: not picking.credit_note_id):
            picking.credit_note_id = False
            move_id = picking._search_invoice()
            if move_id:
                reversed_entry_id = (
                    self.env["account.move"]
                    .sudo()
                    .search([("reversed_entry_id", "=", move_id.id)])
                )
                picking.credit_note_id = reversed_entry_id or False

    def _compute_show_reverse_button(self):
        for picking in self:
            picking.show_reverse_button = False
            if (
                picking.picking_type_id.allow_create_credit_note
                and picking.sale_id
                and picking.state == "done"
                and not picking.credit_note_id
            ):
                move_id = self._search_invoice()
                if move_id:
                    picking.show_reverse_button = True

    # -------------------------------------------------------------------------
    # ACTION METHODS
    # -------------------------------------------------------------------------
    def button_validate(self):
        if self.picking_type_id.allow_create_credit_note and not self.sale_id:
            move_id = (
                self.env["account.move"]
                .sudo()
                .create(
                    {
                        "move_type": "out_refund",
                        "partner_id": self.partner_id.id,
                        "invoice_line_ids": [
                            (
                                0,
                                0,
                                {
                                    "product_id": move_line.product_id.id,
                                    "quantity": move_line.quantity_done,
                                },
                            )
                            for move_line in self.move_ids_without_package.filtered(
                                lambda line: line._origin
                            )
                        ],
                    }
                )
            )
            self.credit_note_id = move_id
        return super(Picking, self).button_validate()

    def action_reverse(self):
        if self.sale_id:
            move_id = self.move_ids_without_package.sale_line_id.invoice_lines.move_id
            action = move_id.action_reverse()
            ctx = eval(action["context"])
            ctx.update(
                {
                    "active_ids": move_id.ids,
                    "active_id": move_id.id,
                    "active_model": "account.move",
                    "default_journal_id": move_id.journal_id.id,
                }
            )
            action["context"] = ctx
            return action

    def action_view_credit_note(self):
        form_view = self.env.ref("account.view_move_form").id
        return {
            "name": _("Credit Note"),
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "view_mode": "form",
            "view_id": form_view,
            "res_id": self.credit_note_id.id,
            "target": "current",
        }
