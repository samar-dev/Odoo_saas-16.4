import logging
import time
from datetime import datetime
from random import uniform

import serial
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)
from odoo.osv import expression

class ScaleReader(models.Model):
    _name = "scale.reader"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Scale Reader"
    _order = "name"

    name = fields.Char(
        string="Sequence Number",
        required=True,
        index=True,
        copy=False,
        readonly=True,
        default='/'
    )
    check_state = fields.Selection(
        [
            ("wait", "To Deliver"),
            ("delivery", "Delivered"),
            ("invoice", "To Invoice"),
            ("par_invoice", "Partial Invoice"),
            ("closed", "Closed"),
        ],
        compute="_compute_check_state",
        store=True,
        string="Etat Facture",
    )

    weight_empty = fields.Float(string="Weight Empty")
    weight_full = fields.Float(string="Weight Full")
    net_weight = fields.Float(
        string="Net Weight", compute="_compute_net_weight", store=True
    )
    remaining_qty = fields.Float(
        string="Remaining Quantity",
        default=0.0,
        compute="_compute_remaining_qty",
        store=True,
    )

    weight_empty_datetime = fields.Datetime(string="Weight Empty")
    weight_full_datetime = fields.Datetime(string="Weight Full")
    vehicle = fields.Char(string="Vehicle")
    is_connected = fields.Boolean(string="Is Connected", default=False)
    weight_empty_check = fields.Boolean(string="")
    weight_full_check = fields.Boolean(string="", default=True)
    scale_settings_id = fields.Many2one("scale.settings", string="Scale Settings")
    lot_number = fields.Char(string="Lot Number")
    transporter_id = fields.Many2one(
        "res.partner",
        string="Transporter",
        required=True,
        change_default=True,
        tracking=True,
        domain="[ '|', ('company_id', '=', company_id), ('company_id', '=', False)]",
        help="You can find a vendor by its Name, TIN, Email or Internal Reference.",
    )
    is_done = fields.Boolean(string=_("Done"), default=False, readonly=True, )

    is_invoiced = fields.Selection(
        [("invoiced", "Facturé"), ("uninvoiced", "Non Facturé")],
        "Etat Facture",
        compute="_compute_is_invoiced",
        store=True,
    )

    invoice_ids = fields.Many2many(
        "account.move",
        string="Vendor Bills",
        relation="scale_reader_account_move_rel",  # optional: custom relation table name
        column1="scale_reader_id",
        column2="account_move_id",
    )

    vendor_id = fields.Many2one(
        "res.partner",
        string="Supplier",
        required=True,
        change_default=True,
        tracking=True,
        domain="[ '|', ('company_id', '=', company_id), ('company_id', '=', False)]",
        help="You can find a vendor by its Name, TIN, Email or Internal Reference.",
    )
    product_id = fields.Many2one("product.product", string="Product", required=True)
    numero_adm = fields.Char(string="N°ADM")
    ac = fields.Char(string="AC")
    k_two = fields.Float(string="K232", digits=(16, 3))
    k_seven = fields.Float(string="K270", digits=(16, 3))
    pesticides = fields.Float(string="Pesticides", digits=(16, 3))
    location_id = fields.Many2one("stock.location", string="Location")
    weighing_slip = fields.Char(string="Weighing Slip")
    company_id = fields.Many2one(
        "res.company", "Company", required=True, default=lambda self: self.env.company
    )

    invoice_id = fields.Many2one(
        "account.move", string="Vendor Bill", ondelete="set null"
    )

    picking_id = fields.Many2one("stock.picking", string="Receipt", readonly=True)

    split_receipt = fields.Boolean(
        string="Répartir la réception sur plusieurs localisations"
    )

    line_ids = fields.One2many(
        "scale.reader.line", "reader_id", string="Détails poids net"
    )

    def make_is_done(self):
        self.write({"is_done": True})

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('scale.reader.sequence') or '/'
        return super(ScaleReader, self).create(vals)

    @api.depends("invoice_id")
    def _compute_is_invoiced(self):
        for record in self:
            if record.invoice_id:
                record.is_invoiced = "invoiced"
            else:
                record.is_invoiced = "uninvoiced"

    @api.depends("invoice_ids", "picking_id", "remaining_qty", "is_done")
    def _compute_check_state(self):
        for record in self:
            if (
                    record.invoice_ids and
                    record.picking_id and
                    (
                            record.remaining_qty == 0 or
                            (record.is_done and record.remaining_qty != 0)
                    )
            ):
                record.check_state = "closed"
            elif record.invoice_ids and record.remaining_qty == 0:
                record.check_state = "invoice"
            elif record.invoice_ids and record.remaining_qty != 0:
                record.check_state = "par_invoice"
            elif record.picking_id and not record.invoice_ids:
                record.check_state = "delivery"
            else:
                record.check_state = "wait"

    @api.depends("weight_empty", "weight_full")
    def _compute_net_weight(self):
        for record in self:
            record.net_weight = record.weight_full - record.weight_empty

    def check_connection(self):
        self.ensure_one()
        settings = self.scale_settings_id
        if not settings:
            _logger.error("No scale settings configured for this reader.")
            self.is_connected = False
            return False

        SERIAL_PORT = settings.ip_address
        BAUD_RATE = settings.port

        try:
            with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
                self.is_connected = True
                _logger.info(f"Successfully connected to the scale on {SERIAL_PORT}.")
                return True
        except Exception as e:
            self.is_connected = False
            _logger.error(f"Connection error on {SERIAL_PORT}: {e}")
            return False

    def read_weight(self, command):
        self.ensure_one()
        if not self.check_connection():
            return None

        settings = self.scale_settings_id
        if not settings:
            _logger.error("Scale settings not configured.")
            return None

        SERIAL_PORT = settings.ip_address
        BAUD_RATE = settings.port

        try:
            with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
                time.sleep(2)  # Let the scale stabilize
                ser.write(command)
                time.sleep(1)
                weight = ser.readline().decode("utf-8").strip()
                _logger.info(f"Weight read from the scale: {weight}")
                return float(weight)
        except Exception as e:
            _logger.error(f"Error reading weight on {SERIAL_PORT}: {e}")
            return None

    def action_get_weight_full(self):
        self.ensure_one()
        self.weight_full_check = False
        self.weight_empty_check = True

        weight = self.read_weight(b"YOUR_FULL_WEIGHT_COMMAND_HERE")  # Replace
        if weight is not None:
            self.weight_full = weight
            self.weight_full_datetime = datetime.now()
            return {
                "warning": {
                    "title": "Weight Retrieved",
                    "message": f"Full weight: {weight}",
                }
            }
        else:
            random_weight_full = uniform(60.0, 100.0)
            self.weight_full = random_weight_full
            self.weight_full_datetime = datetime.now()
            return {
                "warning": {
                    "title": "Connection Error",
                    "message": f"Could not connect to the scale. Random value assigned: {random_weight_full}",
                }
            }

    @api.depends(
        "net_weight",
        "invoice_ids.invoice_line_ids.quantity",
        "invoice_ids.invoice_line_ids.product_id",
        "invoice_ids.invoice_line_ids.scale_id",
    )
    def _compute_remaining_qty(self):
        for scale in self:
            if not scale.is_done:
                total_invoiced_qty = sum(
                    line.quantity
                    for inv in scale.invoice_ids
                    for line in inv.invoice_line_ids
                    if line.product_id.id == scale.product_id.id
                    and (line.scale_id.id == scale.id or not line.scale_id)
                )
                scale.remaining_qty = max(scale.net_weight - total_invoiced_qty, 0.0)

    def action_get_weight_empty(self):
        self.ensure_one()
        self.weight_full_check = False
        self.weight_empty_check = False

        weight = self.read_weight(b"YOUR_EMPTY_WEIGHT_COMMAND_HERE")  # Replace
        if weight is not None:
            self.weight_empty = weight
            self.weight_empty_datetime = datetime.now()
            return {
                "warning": {
                    "title": "Weight Retrieved",
                    "message": f"Empty weight: {weight}",
                }
            }
        else:
            random_weight_empty = uniform(10.0, 50.0)
            self.weight_empty = random_weight_empty
            self.weight_empty_datetime = datetime.now()
            return {
                "warning": {
                    "title": "Connection Error",
                    "message": f"Could not connect to the scale. Random value assigned: {random_weight_empty}",
                }
            }

    def action_create_invoice(self):
        for record in self:
            # Check if already has linked invoices
            previous_qty = 0.0
            for invoice in record.invoice_ids:
                for line in invoice.invoice_line_ids:
                    if line.product_id.id == record.product_id.id:
                        previous_qty += line.quantity
            qty_to_invoice = record.net_weight - previous_qty
            if qty_to_invoice <= 0:
                raise exceptions.UserError("No remaining quantity to invoice.")

            invoice = self.env["account.move"].create(
                {
                    "move_type": "in_invoice",
                    "partner_id": record.vendor_id.id,
                    "invoice_origin": record.name,
                    "invoice_date": record.weight_empty_datetime,
                    "invoice_line_ids": [
                        (
                            0,
                            0,
                            {
                                "product_id": record.product_id.id,
                                "quantity": qty_to_invoice,
                                "price_unit": record.product_id.standard_price,
                                "name": record.product_id.name,
                                "scale_id" : record.id,
                                "account_id": (
                                        record.product_id.property_account_expense_id.id
                                        or record.product_id.categ_id.property_account_expense_categ_id.id
                                ),
                            },
                        ),
                    ],
                }
            )

            # Link the created invoice to the record (add to Many2many)
            record.invoice_ids = [(4, invoice.id)]
            record.remaining_qty = record.net_weight - previous_qty

    def action_create_receipt(self):
        for record in self:
            if record.picking_id:
                raise exceptions.UserError(
                    "Un bon de réception est déjà lié à cet enregistrement."
                )

            if not record.vendor_id:
                raise exceptions.UserError("Fournisseur manquant.")

            if not record.vendor_id.property_stock_supplier:
                raise exceptions.UserError(
                    "Le fournisseur n'a pas de localisation source par défaut définie."
                )

            picking_type = self.env["stock.picking.type"].search(
                [
                    ("code", "=", "incoming"),
                    ("warehouse_id.company_id", "=", self.env.company.id),
                ],
                limit=1,
            )

            if not picking_type:
                raise exceptions.UserError(
                    "Aucun type de picking 'incoming' trouvé pour cette société."
                )

            # Déterminer les lignes de mouvement
            if record.split_receipt:
                if not record.line_ids:
                    raise exceptions.UserError(
                        "Aucune ligne de détail pour la répartition."
                    )
                total_split_weight = sum(
                    line.net_weight_qty for line in record.line_ids
                )
                if (
                        abs(total_split_weight - record.net_weight) != 0
                ):  # tolérance flottant
                    raise exceptions.UserError(
                        "La somme des poids détaillés ({:.2f}) doit être égale au poids net total ({}).".format(
                            total_split_weight, record.net_weight
                        )
                    )
                move_lines = []
                for line in record.line_ids:
                    if (
                            not line.product_id
                            or not line.net_weight_qty
                            or not line.location_id
                    ):
                        raise exceptions.UserError(
                            "Détail incomplet dans une ligne (produit, poids ou localisation)."
                        )
                    move_lines.append(
                        (
                            0,
                            0,
                            {
                                "name": line.product_id.name,
                                "product_id": line.product_id.id,
                                "product_uom_qty": line.net_weight_qty,
                                "product_uom": line.product_id.uom_id.id,
                                "location_id": record.vendor_id.property_stock_supplier.id,
                                "location_dest_id": line.location_id.id,
                            },
                        )
                    )
            else:
                # Mode simple, comme ton code original
                if (
                        not record.product_id
                        or not record.net_weight
                        or not record.location_id
                ):
                    raise exceptions.UserError(
                        "Produit, poids net ou localisation manquant."
                    )
                if record.net_weight <= 0:
                    raise exceptions.UserError("Poids net invalide.")

                move_lines = [
                    (
                        0,
                        0,
                        {
                            "name": record.product_id.name,
                            "product_id": record.product_id.id,
                            "product_uom_qty": record.net_weight,
                            "product_uom": record.product_id.uom_id.id,
                            "location_id": record.vendor_id.property_stock_supplier.id,
                            "location_dest_id": record.location_id.id,
                        },
                    )
                ]

            # Création du picking
            picking = self.env["stock.picking"].create(
                {
                    "partner_id": record.vendor_id.id,
                    "picking_type_id": picking_type.id,
                    "location_id": record.vendor_id.property_stock_supplier.id,
                    "location_dest_id": record.location_id.id,
                    "scheduled_date": fields.Datetime.now(),
                    "origin": record.name,
                    "move_ids_without_package": move_lines,
                }
            )

            record.picking_id = picking.id

            # Confirmer, assigner, renseigner les quantités
            picking.action_confirm()
            picking.action_assign()
            for move_line in picking.move_line_ids:
                if record.line_ids:
                    move_line.qty_done = move_line.move_id.product_uom_qty
                else:
                    move_line.qty_done = record.net_weight
            # Ou record.net_weight si 1 seul produit
            picking.action_generate_lots()
            # Valider le picking
            picking.button_validate()

            # Mise à jour du lot si généré
            stock_moves = picking.move_ids_without_package



            for move in stock_moves:
                if move.move_line_ids and move.move_line_ids[0].lot_id:
                    lot = move.move_line_ids[0].lot_id
                    lot.sudo().write({
                        "name": record.lot_number,
                        "numero_adm": record.numero_adm,
                        "ac": record.ac,
                        "k_two": record.k_two,
                        "k_seven": record.k_seven,
                        "pesticides": record.pesticides,
                    })
                else:
                    raise exceptions.UserError(
                        "Aucun lot généré pour un des mouvements."
                    )

            picking.message_post(body="Réception créée et validée automatiquement.")
            self.sent_message()
            self.remaining_qty = self.net_weight

    @api.model
    def _prepare_invoice_line(self, scale, qty_to_invoice):
        account = (
                scale.product_id.property_account_expense_id
                or scale.product_id.categ_id.property_account_expense_categ_id
        )
        if not account:
            raise UserError(
                _("No expense account defined on product %s")
                % scale.product_id.display_name
            )
        return {
            "product_id": scale.product_id.id,
            "scale_id": scale.id,  # Lien vers le scale
            "name": scale.product_id.display_name,
            "quantity": qty_to_invoice,
            "price_unit": scale.product_id.standard_price,
            "account_id": account.id,
        }

    def action_generate_invoice(self):
        active_ids = self.env.context.get("active_ids", [])
        if not active_ids:
            raise UserError(_("Please select at least one scale to invoice."))

        all_scales = self.browse(active_ids)

        total_remaining_qty = 0.0
        qty_to_invoice_map = {}

        # Pré-calcul qty_to_invoice pour chaque scale
        for scale in all_scales:
            previous_qty = sum(
                line.quantity
                for inv in scale.invoice_ids
                for line in inv.invoice_line_ids
                if line.product_id.id == scale.product_id.id
                and (line.scale_id.id == scale.id or not line.scale_id)
            )
            qty_to_invoice = max(scale.net_weight - previous_qty, 0.0)
            qty_to_invoice_map[scale.id] = qty_to_invoice
            total_remaining_qty += qty_to_invoice

        if total_remaining_qty <= 0:
            raise UserError(
                _("All selected scales have already been invoiced:\n%s")
                % "\n".join(all_scales.mapped("name"))
            )

        # Vérifier fournisseur unique
        partners = all_scales.mapped("vendor_id")
        partners = [p for p in partners if p]  # Éliminer les None
        if len(partners) != 1:
            raise UserError(_("Scales to invoice must all have the same Vendor."))

        partner = partners[0]

        # Génération des lignes de facture
        invoice_lines = [
            (0, 0, self._prepare_invoice_line(scale, qty_to_invoice_map[scale.id]))
            for scale in all_scales
            if qty_to_invoice_map[scale.id] > 0
        ]

        if not invoice_lines:
            raise UserError(
                _("No remaining quantity to invoice for the selected scales.")
            )

        # Création facture
        vals = {
            "move_type": "in_invoice",
            "partner_id": partner.id,
            "invoice_date": fields.Date.context_today(self),
            "invoice_line_ids": invoice_lines,
        }
        invoice = self.env["account.move"].create(vals)

        # Mise à jour des scales
        for scale in all_scales:
            total_invoiced_qty = sum(
                line.quantity
                for inv in (scale.invoice_ids | invoice)
                for line in inv.invoice_line_ids
                if line.product_id.id == scale.product_id.id
                and (line.scale_id.id == scale.id or not line.scale_id)
            )
            new_remaining = max(scale.net_weight - total_invoiced_qty, 0.0)
            scale.write(
                {
                    "invoice_ids": [(4, invoice.id)],
                    "remaining_qty": new_remaining,
                }
            )

        return {
            "name": _("Invoice"),
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "view_mode": "form",
            "res_id": invoice.id,
            "context": {"default_move_type": invoice.move_type},
        }

    def sent_message(self):
        admin_group = self.env.ref("purchase.group_purchase_user")
        user_ids = admin_group.users
        if user_ids:
            channel_name = "Réception Huile"
            message = "<p>Une nouvelle réception a été créée"
            message += " et est en attente d'approbation : "
            message += f'<a href="#" data-oe-model="{self._name}" data-oe-id="{self.id}">{self.name}</a></p>'
            self._base_send_a_message(user_ids, channel_name, message)

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

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """Enable searching by multiple fields: name, weighing_slip, vehicle, lot_number, vendor, product."""
        args = args or []
        if name:
            domain = expression.OR([
                [('name', operator, name)],
                [('weighing_slip', operator, name)],
                [('vehicle', operator, name)],
                [('lot_number', operator, name)],
                [('vendor_id.name', operator, name)],
                [('product_id.name', operator, name)],
                [('net_weight', operator, name)],
            ])
            records = self.search(expression.AND([domain, args]), limit=limit)
            return records.name_get()
        return super(ScaleReader, self).name_search(name=name, args=args, operator=operator, limit=limit)


class NetWeightDetail(models.Model):
    _name = "scale.reader.line"
    _description = "Détail du poids net par localisation"

    reader_id = fields.Many2one("scale.reader", required=True, ondelete="cascade")
    product_id = fields.Many2one("product.product", required=True)
    net_weight_qty = fields.Float(string="Poids net", required=True)
    location_id = fields.Many2one("stock.location", required=True)
