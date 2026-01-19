from odoo import models, fields, api
from odoo.exceptions import UserError


class ProductRecalculateValuation(models.Model):
    _name = "product.recalculate.valuation"
    _description = "Product Recalculate Valuation"

    name = fields.Char("Name")
    product_id = fields.Many2one("product.product", string="Product", required=True)
    date_start = fields.Datetime(string="Start Date")
    date_end = fields.Datetime(
        string="End Date", compute="_compute_last_valuation_date", store=True
    )
    has_backup = fields.Boolean(string="Has Backup", compute="_compute_has_backup")

    @api.depends("product_id")
    def _compute_last_valuation_date(self):
        for record in self:
            if record.product_id:
                last_valuation = self.env["stock.valuation.layer"].search(
                    [("product_id", "=", record.product_id.id)],
                    order="create_date desc",
                    limit=1,
                )
                if last_valuation:
                    record.date_end = last_valuation.create_date
                else:
                    record.date_end = False

    @api.depends("product_id")
    def _compute_has_backup(self):
        for record in self:
            backup_exists = (
                self.env["product.recalculate.backup"].search_count(
                    [("product_id", "=", record.product_id.id)]
                )
                > 0
            )
            record.has_backup = backup_exists

    @staticmethod
    def update_unit_cost(current_avg_cost, unit_cost):
        if unit_cost == 0:
            return current_avg_cost
        difference_percentage = abs((current_avg_cost - unit_cost) / unit_cost) * 100
        if difference_percentage < 3:
            return unit_cost
        else:
            return current_avg_cost

    def action_backup_layers(self):
        layers = self.env["stock.valuation.layer"].search(
            [
                ("product_id", "=", self.product_id.id),
                ("create_date", ">=", self.date_start),
                ("create_date", "<=", self.date_end),
            ]
        )
        if not layers:
            raise UserError("No valuation layers found for the specified criteria.")

        # Remove old backups for this product
        old_backups = self.env["product.recalculate.backup"].search(
            [("product_id", "=", self.product_id.id)]
        )
        old_backups.sudo().unlink()

        self.env["product.recalculate.backup"].sudo().create(
            {
                "product_id": self.product_id.id,
                "backup_data": [
                    (
                        0,
                        0,
                        {
                            "valuation_layer_id": layer.id,
                            "unit_cost": layer.unit_cost,
                            "value": layer.value,
                            "quantity": layer.quantity,
                            "description": layer.description,
                            "remaining_value": layer.remaining_value,
                        },
                    )
                    for layer in layers
                ],
            }
        )
        return {"type": "ir.actions.client", "tag": "reload"}

    def action_restore_layers(self):
        backup = self.env["product.recalculate.backup"].search(
            [("product_id", "=", self.product_id.id)], limit=1
        )
        if not backup:
            raise UserError("No backup found for this product.")

        for data in backup.backup_data:
            layer = self.env["stock.valuation.layer"].browse(data.valuation_layer_id.id)
            layer.sudo().write(
                {
                    "unit_cost": data.unit_cost,
                    "value": data.value,
                    "quantity": data.quantity,
                    "remaining_value": data.remaining_value,
                }
            )
        return {"type": "ir.actions.client", "tag": "reload"}

    def action_recompute_costs(self):
        if self.date_start > self.date_end:
            raise UserError("The start date cannot be after the end date.")

        layers = self.env["stock.valuation.layer"].search(
            [
                ("product_id", "=", self.product_id.id),
                ("create_date", ">=", self.date_start),
                ("create_date", "<=", self.date_end),
            ],
            order="create_date asc",
        )
        if not layers:
            raise UserError("No valuation layers found for the specified criteria.")

        initial_layer = layers[0]
        current_avg_cost = initial_layer.unit_cost
        cumulative_quantity = initial_layer.quantity
        initial_layer.write(
            {
                "unit_cost": current_avg_cost,
                "value": cumulative_quantity * current_avg_cost,
            }
        )

        for layer in layers[1:]:
            new_unit_cost = self.update_unit_cost(current_avg_cost, layer.unit_cost)
            layer.write(
                {
                    "unit_cost": new_unit_cost,
                    "value": layer.quantity * new_unit_cost,
                    "remaining_value": layer.remaining_qty * new_unit_cost,
                }
            )
            cumulative_quantity += layer.quantity

            # *** TA PARTIE COMPTABLE ORIGINALE, INCHANGÉE ***
            if "-" in layer.description:
                reference = layer.description
                account_move = self.env["account.move"].search(
                    [("ref", "ilike", reference)], limit=1
                )
                if not account_move:
                    raise UserError(
                        f"No account.move found with reference: {reference}"
                    )

                if account_move.state == "posted":
                    account_move.button_draft()
                debit_value = abs(layer.value)
                credit_value = abs(layer.value)
                for line in account_move.line_ids:
                    vals = {}
                    if line.debit > 0:
                        vals = {"debit": debit_value, "credit": 0.0}
                    elif line.credit > 0:
                        vals = {"debit": 0.0, "credit": credit_value}
                    if vals:
                        line.with_context(check_move_validity=False).write(vals)
                account_move.action_post()

        return {"type": "ir.actions.client", "tag": "reload"}

    def action_open_backups(self):
        self.ensure_one()
        backups = self.env["product.recalculate.backup"].search(
            [("product_id", "=", self.product_id.id)]
        )
        action = self.env.ref(
            "v__account_imputation.action_product_recalculate_backup"
        ).read()[0]
        action.update(
            {
                "domain": [("id", "in", backups.ids)],
                "context": dict(self.env.context),
            }
        )
        return action


class ProductRecalculateBackup(models.Model):
    _name = "product.recalculate.backup"
    _description = "Backup of Product Valuation Layers"

    product_id = fields.Many2one("product.product", string="Product", required=True)
    backup_data = fields.One2many(
        "product.recalculate.backup.line", "backup_id", string="Backup Data"
    )
    backup_date = fields.Datetime(string="Backup Date", default=fields.Datetime.now)


class ProductRecalculateBackupLine(models.Model):
    _name = "product.recalculate.backup.line"
    _description = "Backup Line for Product Valuation Layer"

    backup_id = fields.Many2one(
        "product.recalculate.backup", string="Backup Reference", required=True
    )
    valuation_layer_id = fields.Many2one(
        "stock.valuation.layer", string="Valuation Layer", required=True
    )
    description = fields.Char(string="Description")
    unit_cost = fields.Float(string="Unit Cost", digits=(16, 3))
    value = fields.Float(string="Value", digits=(16, 3))
    quantity = fields.Float(string="Quantity", digits=(16, 3))
    remaining_value = fields.Float(string="Remaining Value", digits=(16, 3))
