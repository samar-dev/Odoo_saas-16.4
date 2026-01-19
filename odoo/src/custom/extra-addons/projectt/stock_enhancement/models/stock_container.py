from odoo import models, fields, api


class StockContainer(models.Model):
    _name = "stock.container"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Conteneur de stock"  # Translation of "Stock Container"

    name = fields.Char("Nom Lot", required=True)  # Container Name
    reference = fields.Char("Référence du conteneur")  # Container Reference
    description = fields.Text("Description")  # Description
    capacity = fields.Float(
        "Capacité",
        help="Capacité du conteneur en volume ou en poids",  # Capacity description
    )
    product_name = fields.Char("Article", required=True)  # Container Name
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("validated", "Validated"),
        ],
        default="draft",
        string="Statu",
    )

    # Change the relation from stock.move to stock.picking
    picking_ids = fields.Many2many(
        "stock.picking",
        "stock_picking_container_rel",  # Relation table name
        "container_id",  # Field for stock.container
        "picking_id",  # Field for stock.picking
        string="Expéditions",  # Pickings
    )

    # One2many relation to stock.container.line
    container_line_ids = fields.One2many(
        "stock.container.line",
        "container_id",
        string="Lignes du conteneur",  # Container Lines
    )

    container_nbr_pallet = fields.Float(
        string="Nombre de palettes", compute="_compute_container_nbr_pallet", store=True
    )

    # Poids calculé en fonction du poids brut
    container_weight = fields.Float(
        string="Poids du conteneur", compute="_compute_container_weight", store=True
    )

    type_of_container = fields.Selection(
        [
            ("flexitank", "Flexitank"),
            ("container", "Conteneur"),
            ("Citerne", "Citerne"),
        ],
        default="container",
        string="Type de Contenant",
    )

    container_line_ids = fields.One2many(
        "stock.container.line",
        "container_id",
        string="Lignes du conteneur",  # Container Lines
    )
    picking_product_ids = fields.Many2many(
        "product.product",
        string="les expéditions",  # Products in Pickings
        compute="_compute_picking_product_ids",
    )

    @api.depends("picking_ids.move_ids.gross_weight")
    def _compute_container_weight(self):
        for container in self:
            total_gross_weight = sum(
                move.gross_weight
                for picking in container.picking_ids
                for move in picking.move_ids
            )
            container.container_weight = (
                total_gross_weight  # Sum of the gross weight of the moves
            )

    @api.depends("picking_ids.move_ids.nbr_pallet", "capacity")
    def _compute_container_nbr_pallet(self):
        for container in self:
            total_nbr_pallet = sum(
                move.nbr_pallet
                for picking in container.picking_ids
                for move in picking.move_ids
            )
            container.container_nbr_pallet = (
                total_nbr_pallet  # Sum of the number of pallets
            )

    # Compute field to get the list of product IDs from picking_ids
    @api.depends("picking_ids", "container_line_ids.product_id")
    def _compute_picking_product_ids(self):
        for container in self:
            # Get all products from the moves of the related pickings
            available_product_ids = set(
                move.product_id.id
                for picking in container.picking_ids
                for move in picking.move_ids
            )

            # Update the computed field to only show available products (no exclusion of selected products)
            container.picking_product_ids = [(6, 0, list(available_product_ids))]

    def action_validate_container(self):
        for record in self:
            if record.state == "draft":
                record.state = "validated"
            else:
                record.state = "draft"


class StockContainerLine(models.Model):
    _name = "stock.container.line"
    _description = "Ligne de conteneur de stock"  # Stock Container Line

    container_id = fields.Many2one(
        "stock.container", string="Conteneur", required=True
    )  # Container
    product_id = fields.Many2one(
        "product.product",
        string="Produit",
    )  # Product
    quantity = fields.Float("Quantité", default=0)  # Quantity

    product_packaging_qty = fields.Integer(string="Carton", default=0)

    product_packaging_id = fields.Many2one('product.packaging', string='Packaging',
                                           domain="[('purchase', '=', True), ('product_id', '=', product_id)]",
                                           check_company=True,
                                           compute="_compute_product_packaging_id", store=True, readonly=False)

    flexitank_number = fields.Char("N° Flexitank")  # Numero du Flexitank
    plombs_number = fields.Char("N° Plombs")  # Numero du Flexitank
    container_number = fields.Char("N° Conteneur")  # Numero du Flexitank
    citerne_number = fields.Char("N° Citerne")  # Numero du Flexitank

    net_weight = fields.Float(
        string="Net weight",
    )

    company_id = fields.Many2one(
        "res.company",
        string="Société",
        required=True,
        default=lambda self: self.env.company,
    )

    gross_weight = fields.Float(
        string="Gross weight",
    )

    def _compute_product_packaging_id(self):
        for line in self:
            if line.product_id and line.quantity:
                suggested_packaging = line.product_id.packaging_ids.filtered(
                    lambda p: (p.product_id.company_id <= p.company_id <= line.company_id)
                )
                line.product_packaging_id = (
                    suggested_packaging[0]
                    if suggested_packaging
                    else line.product_packaging_id
                )

    @api.onchange("product_packaging_id", "product_packaging_qty")
    def _computeçproduct_packaging_qty(self):
        for recod in self:
            recod.quantity = recod.product_packaging_qty * recod.product_packaging_id.qty

    @api.onchange("net_weight")
    def _compute_gross_weight(self):
        for record in self:
            record.gross_weight = record.net_weight + 130
