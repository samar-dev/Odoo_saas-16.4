from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    x_customer_type = fields.Selection(
        related="partner_id.x_customer_type", string="Customer type"
    )
    # order
    x_order_number = fields.Char(string="Order number")
    x_order_date = fields.Date(string="Order date")
    x_batch_number = fields.Char(string="Numéro de lot")
    x_other_reference = fields.Char(string="Other reference")
    # contract
    x_contract_number = fields.Char(string="Contract number")
    x_contract_date = fields.Date(string="Contract date")
    # transport
    x_loading_port = fields.Char(string="Loading port")
    x_unloading_port = fields.Char(string="Unloading port")
    x_transport_by = fields.Selection(
        [("land", "Land"), ("air", "Air"), ("sea", "Sea")], string="Transport by"
    )
    x_exporter_manufacturer = fields.Char(string="Exporter / Manufacturer")
    x_customer_invoice_recipient = fields.Char(string="Customer invoice / Recipient")
    x_party_to_inform = fields.Char(
        string="Party to inform (if other than the recipient)"
    )
    x_plan_number = fields.Char(string="Plan number")
    x_flexitank_number = fields.Char(string="Flexitank number")
    x_citerne_number = fields.Char(string="Citerne number")
    x_container_size = fields.Float(string="Container size")
    x_ship_name = fields.Char(string="Ship name")
    x_container_number = fields.Char(string="Container number")
    sum_net_weight = fields.Float(
        string=_("Sum Net weight"), compute="_compute_sum_weight", store=True
    )
    sum_gross_weight = fields.Float(
        string=_("Sum Gross weight"), compute="_compute_sum_weight", store=True
    )
    sum_pallet = fields.Float(
        string=_("Sum Pallet"), compute="_compute_sum_pallet", store=True
    )

    sum_product_packaging_qty = fields.Float(
        string=_("Sum Carton"), compute="_compute_sum_product_packaging_qty", store=True
    )
    x_real_pallet_number = fields.Integer(string="Real pallets number")
    x_show_nbpallet = fields.Boolean(string="Afficher la palette", default=False)

    type_de_palette = fields.Selection(
        [
            ("normal", "Palette normale"),
            ("calculee", "Palette calculée"),
        ],
        default="normal",  # Valeur par défaut pour le nouveau champ
        string="Type de palette",
    )

    type_of_delivery = fields.Selection(
        [
            ("vrac_c", "Vrac Citerne"),
            ("vrac_f", "Vrac Flexitank"),
            ("conditionner", "Conditionner"),
        ],
        default="vrac_c",
        string="Type de livraison",
    )

    customer_bank_id = fields.Many2one(
        string="Banque",
        comodel_name="res.partner.bank",
        readonly=False,
        store=True,
    )

    @api.depends(
        "order_line.net_weight", "order_line.gross_weight", "x_real_pallet_number"
    )
    def _compute_sum_weight(self):
        for order in self:
            pallet_weight = self.env.company.pallet_weight
            order.sum_net_weight = sum(order.order_line.mapped("net_weight"))
            order.sum_gross_weight = sum(order.order_line.mapped("gross_weight"))

    @api.depends("order_line.nbr_pallet")
    def _compute_sum_pallet(self):
        for order in self:
            order.sum_pallet = sum(order.order_line.mapped("nbr_pallet"))

    @api.depends("order_line.product_packaging_qty")
    def _compute_sum_product_packaging_qty(self):
        for order in self:
            order.sum_product_packaging_qty = sum(
                order.order_line.mapped("product_packaging_qty")
            )

    @api.onchange("partner_shipping_id")
    def _oncchange_partner_shipping_id(self):
        for order in self:
            order.x_exporter_manufacturer = order.company_id.name
            order.x_customer_invoice_recipient = order.partner_id.name
            order.x_party_to_inform = order.partner_shipping_id.name

    @api.onchange("order_line")
    def _onchange_order_line(self):
        if len(self._origin.order_line) < len(self.order_line):
            if (
                self.order_line[-1].product_template_id
                in self.order_line[:-1].product_template_id
                and not self.order_line[-1].duplicate
            ):
                self.order_line[-1].duplicate = True
                return {
                    "warning": {
                        "title": _("Attention"),
                        "message": _(
                            "Article duplication detected! Please check your entry"
                        ),
                    }
                }

    @api.onchange("x_transport_by")
    def update_order_date(self):
        self.x_order_date = self.date_order

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()

        # Check if res is True (indicating success)
        if res:
            # Assuming you want to check the sale order itself, not a list
            if self.partner_id.x_customer_type in [
                "prospect_client",
                "prospect_fournisseur",
            ]:
                raise ValidationError(
                    _(
                        "Action ne peut pas être effectuée car le type de client est défini sur 'Prospect Client' ou 'Prospect Fournisseur'. Veuillez mettre à jour le type de client avant de continuer."
                    )
                )
        return res


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def create_invoices(self):
        res = super(SaleAdvancePaymentInv, self).create_invoices()

        # Loop over all sale orders related to this record
        for order in self.sale_order_ids:
            if order.partner_id.x_invoice_policy == "delivery":
                pickings = order.picking_ids.filtered(lambda p: p.state != "done")
                if pickings:
                    raise ValidationError(
                        "Impossible de créer la facture : le client a une politique de facturation sur livraison "
                        "et toutes les livraisons ne sont pas encore terminées."
                    )

            # Search for existing invoices linked to the sale order
            invoices = self.env["account.move"].search(
                [
                    ("invoice_origin", "=", order.name),
                    ("move_type", "in", ("out_invoice", "out_refund")),
                ]
            )

            # If the invoice policy is not based on delivery, skip further processing
            if order.partner_id.x_invoice_policy != "delivery":
                continue

            # Iterate through each invoice and its lines
            for invoice in invoices:
                lines_to_remove = []
                for line in invoice.invoice_line_ids:
                    sale_line = line.sale_line_ids and line.sale_line_ids[0] or None
                    if sale_line and sale_line.order_id == order:
                        if sale_line.qty_delivered <= 0:
                            lines_to_remove.append(line)
                        else:
                            line.quantity = sale_line.qty_delivered

                # Remove lines where qty_delivered is 0 or less
                for line in lines_to_remove:
                    line.unlink()

        return res


class PivotInheritReport(models.Model):
    _inherit = "sale.report"
    sum_net_weight = fields.Float(
        string=_("Poids Nets"), compute="_compute_sum_weight", store=True
    )
    sum_gross_weight = fields.Float(
        string=_("Poids Bruts"), compute="_compute_sum_weight", store=True
    )

    def _compute_sum_weight(self):
        for order in self:
            pallet_weight = self.env.company.pallet_weight
            order.sum_net_weight = sum(order.order_line.mapped("net_weight"))
            order.sum_gross_weight = sum(order.order_line.mapped("gross_weight"))

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res["sum_net_weight"] = "l.net_weight"
        res["sum_gross_weight"] = "l.gross_weight"
        return res

    def _group_by_sale(self):
        res = super()._group_by_sale()
        res += """,
            l.net_weight"""
        res += """,
                    l.gross_weight"""
        return res
