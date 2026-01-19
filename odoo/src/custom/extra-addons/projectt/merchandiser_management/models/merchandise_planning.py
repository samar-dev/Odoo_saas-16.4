from odoo import api, fields, models


class MerchandisePlanning(models.Model):
    _name = "merchandise.planning"
    _description = "Merchandise Planning"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "start_datetime desc, id desc"
    _rec_name = "name"

    # -------------------
    # Basic Info
    # -------------------
    partner_id = fields.Many2one("res.partner", string="Partner")
    planning_id = fields.Many2one(
        "planning.slot", string="Planning", ondelete="cascade"
    )
    name = fields.Char(string="Name", compute="_compute_name")
    resource_id = fields.Many2one(related="planning_id.resource_id")
    resource_type = fields.Selection(related="resource_id.resource_type")
    employee_id = fields.Many2one(related="planning_id.employee_id")
    role_id = fields.Many2one(related="planning_id.role_id")
    start_datetime = fields.Datetime(related="planning_id.start_datetime")
    end_datetime = fields.Datetime(related="planning_id.end_datetime")
    allocated_hours = fields.Float(related="planning_id.allocated_hours")
    allocated_percentage = fields.Float(related="planning_id.allocated_percentage")
    last_visit_date = fields.Date(
        string="Visit N-1 Date", compute="_compute_last_visit_date"
    )
    company_id = fields.Many2one(related="planning_id.company_id")

    attachment_ids = fields.One2many(
        "ir.attachment",
        "res_id",
        string="Attachments",
        domain=[("res_model", "=", "merchandise.planning")],
    )

    # -------------------
    # Assortment + Store
    # -------------------
    assortment_id = fields.Many2one("assortment", string="Assortment", required=True)
    store_id = fields.Many2one("res.partner.store", string="Store")
    store_ids = fields.Many2many(
        "res.partner.store", string="Stores", compute="_compute_store_ids"
    )

    # -------------------
    # Lines
    # -------------------
    merchandise_planning_line = fields.One2many(
        "merchandise.planning.line",
        "merchandise_planning_id",
        string="Merchandise Planning Line",
    )
    concurrent_line = fields.One2many(
        "concurrent.line", "merchandise_planning_id", string="Concurrent Line"
    )

    # -------------------
    # State + Cancellation
    # -------------------
    state = fields.Selection(
        [("draft", "Draft"), ("done", "Done"), ("cancelled", "Cancelled")],
        string="Status",
        default="draft",
        readonly=True,
    )
    reason = fields.Text(string="Cancellation reason")

    # -------------------
    # Compute Methods
    # -------------------
    def _compute_name(self):
        for record in self:
            record.name = "%(store_id)s - %(assortment_name)s" % {
                "store_id": record.store_id.name if record.store_id else "",
                "assortment_name": (
                    record.assortment_id.name if record.assortment_id else ""
                ),
            }

    def _compute_last_visit_date(self):
        for record in self:
            # If record is new (unsaved), we cannot search by id
            if not record.id:
                record.last_visit_date = (
                    record.end_datetime.date() if record.end_datetime else False
                )
                continue

            last_visit = self.env["merchandise.planning"].search(
                [
                    ("id", "!=", record.id),
                    ("assortment_id", "=", record.assortment_id.id),
                    ("resource_id", "=", record.resource_id.id),
                ],
                order="id desc",
                limit=1,
            )
            if last_visit:
                record.last_visit_date = (
                    last_visit.end_datetime.date() if last_visit.end_datetime else False
                )
            else:
                record.last_visit_date = (
                    record.end_datetime.date() if record.end_datetime else False
                )

    @api.depends("assortment_id")
    def _compute_store_ids(self):
        for record in self:
            stores = self.env["res.partner.store"]
            if record.assortment_id:
                for template in record.assortment_id.product_template_ids:
                    stores |= self.env["res.partner.store"].search(
                        [
                            ("partner_id", "=", record.partner_id.id),
                            ("product_ids", "in", template.ids),
                        ]
                    )
            record.store_ids = stores

    # -------------------
    # Onchange Methods
    # -------------------
    @api.onchange("partner_id")
    def _onchange_partner(self):
        for record in self:
            return {
                "domain": {
                    "assortment_id": [("partner_id", "=", record.partner_id.id)],
                    "store_id": [("partner_id", "=", record.partner_id.id)],
                }
            }

    @api.onchange("assortment_id", "store_id")
    def _onchange_assortment_store(self):
        for record in self:
            if not record.assortment_id or not record.store_id:
                return

            # 1️⃣ Archive all existing lines (requires 'active' field)
            record.merchandise_planning_line.write({"active": False})

            # 2️⃣ Filter templates by store
            templates = record.assortment_id.product_template_ids.filtered(
                lambda t: t in record.store_id.product_ids
            )

            new_lines = []

            for template in templates:
                # Use variants if they exist, otherwise use template as pseudo-variant
                variants = template.product_variant_ids or [template]

                for variant in variants:
                    # Skip if variant/template does not exist
                    if not variant.exists():
                        continue

                    # Check if line already exists for this product
                    existing_line = record.merchandise_planning_line.filtered(
                        lambda l: l.product_id.id == getattr(variant, "id", 0)
                    )
                    if existing_line:
                        # Reactivate old line
                        existing_line.active = True
                    else:
                        # Create new line
                        new_lines.append(
                            (
                                0,
                                0,
                                {
                                    "product_id": getattr(variant, "id", False),
                                    "product_name": getattr(
                                        variant, "name", template.name
                                    ),
                                    "barcode": getattr(variant, "barcode", False),
                                    "merchandise_planning_id": self.id,
                                    "assortment_id": self.assortment_id.id,
                                    "store_id": self.store_id.id,
                                    "active": True,
                                },
                            )
                        )

            # 3️⃣ Assign new lines (existing lines already reactivated)
            if new_lines:
                record.merchandise_planning_line = new_lines

    # -------------------
    # Buttons
    # -------------------
    def button_cancel(self):
        return {
            "name": "Add cancellation reason",
            "view_mode": "form",
            "res_model": "cancellation.reason.wizard",
            "view_id": self.env.ref(
                "merchandiser_management.view_cancellation_reason_wizard_form"
            ).id,
            "type": "ir.actions.act_window",
            "context": {"active_ids": self.ids},
            "target": "new",
        }

    def button_done(self):
        self.write({"state": "done"})

    def button_draft(self):
        self.write({"state": "draft"})
