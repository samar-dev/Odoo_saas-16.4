from odoo import fields, models, api


class QualityCheck(models.Model):
    _inherit = "quality.check"

    quality_state = fields.Selection(
        selection_add=[("validated", "Validated By RMQ")]
    )

    expiration_date = fields.Datetime(
        string='Expiration Date', compute='_compute_expiration_date', store=True
    )

    date_done = fields.Datetime(
        string='Date Done',
        compute='_compute_date_done',
        store=True,
        readonly=True,
        compute_sudo=True,
    )

    checklist_ids = fields.One2many('quality.checklist.emballage', 'quality_check_id', string="Quality Check")

    quality_type = fields.Char(
        string="Type Opération",
        compute="_compute_quality_type",
        store=True,
    )

    picking_partner_display = fields.Char(
        string="Vendor/Customer (Display)",
        compute='_compute_picking_partner_display',
        store=True,
    )

    lot_producing_id = fields.Many2one(
        'stock.lot', string='Lot', compute='_compute_lot_producing_id',
        store=True
    )

    picking_name = fields.Char("Nom", compute='_compute_picking_name')

    production_date = fields.Date(
        string='Production Date', compute='_compute_production_date', store=True
    )

    production_planning_reference = fields.Char(
        string='Planning Ref', compute='_compute_production_planning_reference',
        store=True
    )
    related_picking_name = fields.Char(
        string="Transfert",
        compute="_compute_related_picking_name",
        store=True,
    )
    related_picking_id = fields.Many2one(
        'stock.picking',
        string="Transfert",
        compute="_compute_related_picking_name",
        store=True,
    )

    related_picking_date_done = fields.Datetime(
        string="Date Transfert",
        compute="_compute_related_picking_name",
        store=True,
    )
    related_picking_partner = fields.Many2one(
        'res.partner',
        string="Fournisseur",
        compute="_compute_related_picking_name",
        store=True,
    )

    origin = fields.Char(string='Origin', compute='_compute_origin', store=True)

    x_point_id = fields.Char(
        string='Titre',
        compute='_compute_x_point_id',
        store=True,
    )

    @api.depends('point_id')
    def _compute_x_point_id(self):
        for check in self:
            check.x_point_id = check.point_id.title or ""

    @api.depends('picking_id', 'picking_id.partner_id', 'picking_id.origin')
    def _compute_related_picking_name(self):
        StockPicking = self.env['stock.picking']
        for check in self:
            check.related_picking_name = False
            check.related_picking_date_done = False
            check.related_picking_partner = False
            check.related_picking_id = False
            if check.picking_id and check.picking_id.origin:
                # Find another picking with the same origin and same vendor, exclude current picking
                other_picking = StockPicking.search([
                    ('origin', '=', check.picking_id.origin),
                    ('id', '!=', check.picking_id.id)
                ], limit=1)
                if other_picking:
                    check.related_picking_id = other_picking
                    check.related_picking_name = other_picking.name
                    check.related_picking_date_done = other_picking.date_done
                    check.related_picking_partner = other_picking.partner_id

    def button_validate(self):
        self.quality_state = "validated"

    def action_generate_checklist(self):
        self.ensure_one()

        vals = {
            'name': f"{self.name or 'Check'}",
            'quality_check_id': self.id,
        }

        # If you want to use sequence here instead of fixed name:
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('quality.checklist.emballage') or 'New'

        new_checklist = self.env['quality.checklist.emballage'].create(vals)

        return {
            'type': 'ir.actions.act_window',
            'name': 'Checklist Emballage',
            'res_model': 'quality.checklist.emballage',
            'view_mode': 'form',
            'res_id': new_checklist.id,
            'target': 'current',
        }

    @api.depends('production_id')
    def _compute_expiration_date(self):
        for record in self:
            if record.production_id and record.production_id.lot_producing_id:
                record.expiration_date = record.production_id.lot_producing_id.expiration_date
            else:
                record.expiration_date = False

    @api.depends('picking_id', 'production_id')
    def _compute_quality_type(self):
        for record in self:
            if record.picking_id and not record.production_id:
                record.quality_type = record.picking_id.picking_type_id.name
            elif record.production_id and not record.picking_id:
                record.quality_type = 'Fabrication'
                record.product_id = record.production_id.product_id.id
            else:
                record.quality_type = 'Interne'

    @api.depends('picking_id')
    def _compute_date_done(self):
        for record in self:
            record.date_done = record.picking_id.date_done if record.picking_id else False

    @api.depends('picking_id.partner_id.name', 'production_id.origin')
    def _compute_picking_partner_display(self):
        for record in self:
            if record.picking_id and record.picking_id.partner_id:
                record.picking_partner_display = record.picking_id.partner_id.name
            else:
                record.picking_partner_display = record.production_id.origin or ''

    @api.depends('picking_id')
    def _compute_picking_name(self):
        for record in self:
            record.picking_name = record.picking_id.name if record.picking_id else False

    @api.depends('production_id')
    def _compute_lot_producing_id(self):
        for record in self:
            record.lot_producing_id = record.production_id.lot_producing_id.id if record.production_id and record.production_id.lot_producing_id else False

    @api.depends('production_id')
    def _compute_production_date(self):
        for rec in self:
            rec.production_date = rec.production_id.lot_producing_id.production_date if rec.production_id and rec.production_id.lot_producing_id else False

    @api.depends('production_id')
    def _compute_production_planning_reference(self):
        for rec in self:
            rec.production_planning_reference = rec.production_id.production_planning_reference if rec.production_id else False

    @api.depends('production_id')
    def _compute_origin(self):
        for rec in self:
            rec.origin = rec.production_id.origin if rec.production_id else False
