# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta
import itertools

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.osv.expression import AND


# ---------------------------------------------------------
# Budgets
# ---------------------------------------------------------
class ProductAccountBudgetPost(models.Model):
    _name = "purchase.budget.post"
    _order = "name"
    _description = "Budgetary Position"

    name = fields.Char("Name", required=True)
    account_ids = fields.Many2many(
        "product.product",
        "purchase_budget_rel",
        "budget_id",
        "product_id",
        "Products",
        check_company=True,
        domain="[('detailed_type', '=', 'product')]",
    )
    produc_qty = fields.Integer("Qnt")
    company_id = fields.Many2one(
        "res.company", "Company", required=True, default=lambda self: self.env.company
    )

    def _check_account_ids(self, vals):
        # Raise an error to prevent the account.budget.post to have not specified account_ids.
        # This check is done on create because require=True doesn't work on Many2many fields.
        if "account_ids" in vals:
            account_ids = self.new(
                {"account_ids": vals["account_ids"]}, origin=self
            ).account_ids
        else:
            account_ids = self.account_ids

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._check_account_ids(vals)
        return super().create(vals_list)

    def write(self, vals):
        self._check_account_ids(vals)
        return super(ProductAccountBudgetPost, self).write(vals)


class ProductCrossoveredBudget(models.Model):
    _name = "purchase.crossovered.budget"
    _description = "Budget"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        "Budget Name", required=True, states={"done": [("readonly", True)]}
    )
    user_id = fields.Many2one(
        "res.users", "Responsible", default=lambda self: self.env.user
    )
    department_id = fields.Many2one("hr.department", string="Department")
    date_from = fields.Date("Start Date", states={"done": [("readonly", True)]})
    date_to = fields.Date("End Date", states={"done": [("readonly", True)]})
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirm", "Confirmed"),
            ("validate", "Validated"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        "Status",
        default="draft",
        index=True,
        required=True,
        readonly=True,
        copy=False,
        tracking=True,
    )
    crossovered_budget_line = fields.One2many(
        "purchase.crossovered.budget.lines",
        "purchase_crossovered_budget_id",
        "Budget Lines",
        states={"done": [("readonly", True)]},
        copy=True,
    )

    component_line_ids = fields.One2many(
        "budget.component.line",
        "crossovered_budget_id",
        string="Component Lines",
        compute="_compute_create_components",
        store=True,
    )
    company_id = fields.Many2one(
        "res.company", "Company", required=True, default=lambda self: self.env.company
    )

    @api.constrains("crossovered_budget_line")
    def _check_planned_amount(self):
        for record in self.crossovered_budget_line:
            if record.planned_amount <= 0:
                raise ValidationError(
                    _("The planned amount must be greater than zero.")
                )

    def action_purchase_budget_confirm(self):
        self.write({"state": "confirm"})
        for budget in self:
            # Clear previous component lines when recomputing
            existing_component_lines = self.env["budget.component.line"].search(
                [("crossovered_budget_id", "=", budget.id)]
            )
            existing_component_lines.unlink()

            # Dictionary to hold aggregated data for each product
            aggregated_data = {}

            # Loop through each budget line
            for cdl_line in budget.crossovered_budget_line:
                # Loop through each BOM related to the product
                for bom in cdl_line.product_id.bom_ids:
                    # Loop through each BOM line (the components)
                    for bom_line in bom.bom_line_ids:
                        product = bom_line.product_id
                        component_name = product.name
                        component_quantity = (
                            bom_line.product_qty * cdl_line.planned_amount
                        )
                        product_uom_id = bom_line.product_uom_id.name  # UOM name
                        product_crt_qty = bom.product_qty  # Product quantity
                        product_categ = product.categ_id.name
                        component_cost = (
                            bom_line.product_qty
                            * cdl_line.planned_amount
                            * product.standard_price
                        )

                        # If product already in aggregated_data, update the values
                        if product.id not in aggregated_data:
                            aggregated_data[product.id] = {
                                "component_name": component_name,
                                "quantity": 0,
                                "uom_name": product_uom_id,
                                "product_crt_qty": product_crt_qty,
                                "category_name": product_categ,
                                "cost": 0,
                            }

                        # Aggregate the values
                        aggregated_data[product.id]["quantity"] += component_quantity
                        aggregated_data[product.id]["cost"] += component_cost

            # Loop through aggregated data and create component lines
            for product_id, data in aggregated_data.items():
                # Fetch actual stock from stock.quant (considering specific location)
                # Fetch all internal locations
                internal_locations = self.env["stock.location"].search(
                    [("usage", "=", "internal")]
                )

                # Collect all stock quants for the product in all internal locations
                actual_stock = sum(
                    quant.quantity
                    for quant in self.env["stock.quant"].search(
                        [
                            ("product_id", "=", product_id),
                            (
                                "location_id",
                                "in",
                                internal_locations.ids,
                            ),  # Filter by internal locations
                        ]
                    )
                )
                # Calculate the quantity to be purchased (needed quantity - actual stock)
                quantity_to_purchase = (
                    data["quantity"] - actual_stock
                    if data["quantity"] > actual_stock
                    else 0
                )

                # Add quantity_to_purchase to the data dictionary
                data["quantity_to_purchase"] = quantity_to_purchase
                data["actual_stock"] = actual_stock

                # Create the component line
                self.env["budget.component.line"].create(
                    {
                        "crossovered_budget_id": budget.id,
                        "component_name": data["component_name"],
                        "quantity": data["quantity"],
                        "uom_name": data["uom_name"],
                        "product_crt_qty": data["product_crt_qty"],
                        "category_name": data["category_name"],
                        "cost": data["cost"],
                        "quantity_to_purchase": data["quantity_to_purchase"],
                        "actual_stock": data["actual_stock"],
                        # Add this field to track the quantity to be purchased
                    }
                )

    def action_purchase_budget_draft(self):
        self.write({"state": "draft"})

    def action_purchase_budget_validate(self):
        self.write({"state": "validate"})

    def action_purchase_budget_cancel(self):
        self.write({"state": "cancel"})

    def action_purchase_budget_done(self):
        self.write({"state": "done"})


class ProductCrossoveredBudgetLines(models.Model):
    _name = "purchase.crossovered.budget.lines"
    _description = "Product Budget Line"

    name = fields.Char(compute="_compute_line_name")
    purchase_crossovered_budget_id = fields.Many2one(
        "purchase.crossovered.budget",
        "Budget",
        ondelete="cascade",
        index=True,
        required=True,
    )
    analytic_account_id = fields.Many2one(
        "account.analytic.account", "Analytic Account"
    )
    analytic_plan_id = fields.Many2one(
        "account.analytic.plan",
        "Analytic Plan",
        related="analytic_account_id.plan_id",
        readonly=True,
    )
    product_id = fields.Many2one(
        "product.product",
        required=True,
        domain="[('detailed_type', '=', 'product')]",
    )
    general_budget_id = fields.Many2one("purchase.budget.post", "Budgetary Position")
    date_from = fields.Date("Start Date", required=True)
    date_to = fields.Date("End Date", required=True)
    paid_date = fields.Date("Estimated Date")
    currency_id = fields.Many2one(
        "res.currency", related="company_id.currency_id", readonly=True
    )
    planned_amount = fields.Float(
        "Planned QNT",
        required=True,
        help="Adjust the quantities based on product units. Record a positive figure for revenue and a negative figure for costs, reflecting the number of units involved.",
    )
    practical_amount = fields.Float(
        compute="_compute_practical_amount",
        string="Practical QNT",
        help="Quantity actually earned/spent.",
    )
    theoritical_amount = fields.Float(
        compute="_compute_theoritical_amount",
        string="Theoretical QNT",
        help="Quantity you are expected to have earned/spent by this date.",
        precision_digits=3,
    )
    percentage = fields.Float(
        compute="_compute_percentage",
        string="Achievement",
        help="Comparison between actual and expected quantities. This measure indicates whether you are under or over budget.",
    )
    company_id = fields.Many2one(
        related="purchase_crossovered_budget_id.company_id",
        comodel_name="res.company",
        string="Company",
        store=True,
        readonly=True,
    )
    is_above_budget = fields.Boolean(compute="_is_above_budget")
    crossovered_budget_state = fields.Selection(
        related="purchase_crossovered_budget_id.state",
        string="Budget State",
        store=True,
        readonly=True,
    )

    @api.model
    def _read_group(
        self,
        domain,
        groupby=(),
        aggregates=(),
        having=(),
        offset=0,
        limit=None,
        order=None,
    ):
        SPECIAL = {"practical_amount:sum", "theoritical_amount:sum", "percentage:sum"}
        if SPECIAL.isdisjoint(aggregates):
            return super()._read_group(
                domain, groupby, aggregates, having, offset, limit, order
            )

        base_aggregates = [
            *(agg for agg in aggregates if agg not in SPECIAL),
            "id:recordset",
        ]
        base_result = super()._read_group(
            domain, groupby, base_aggregates, having, offset, limit, order
        )

        # base_result = [(a1, b1, records), (a2, b2, records), ...]
        result = []
        for *other, records in base_result:
            for index, spec in enumerate(itertools.chain(groupby, aggregates)):
                if spec in SPECIAL:
                    field_name = spec.split(":")[0]
                    other.insert(index, sum(records.mapped(field_name)))
            result.append(tuple(other))

        return result

    def _is_above_budget(self):
        for line in self:
            if line.theoritical_amount >= 0:
                line.is_above_budget = line.practical_amount > line.theoritical_amount
            else:
                line.is_above_budget = line.practical_amount < line.theoritical_amount

    @api.depends(
        "purchase_crossovered_budget_id", "general_budget_id", "analytic_account_id"
    )
    def _compute_line_name(self):
        # just in case someone opens the budget line in form view
        for record in self:
            computed_name = record.purchase_crossovered_budget_id.name
            if record.general_budget_id:
                computed_name += " - " + record.general_budget_id.name
            if record.analytic_account_id:
                computed_name += " - " + record.analytic_account_id.name
            record.name = computed_name

    def _compute_practical_amount(self):
        for line in self:
            if not line.product_id:
                line.practical_amount = 0.0
                continue

            date_from = line.date_from
            date_to = line.date_to

            stock_move_obj = self.env["stock.move"]
            domain = [
                ("product_id", "=", line.product_id.id),
                ("date", ">=", date_from),
                ("date", "<=", date_to),
                ("picking_type_id.code", "=", "mrp_operation"),
            ]

            where_query = stock_move_obj._where_calc(domain)
            stock_move_obj._apply_ir_rules(where_query, "read")

            from_clause, where_clause, where_clause_params = where_query.get_sql()

            query = f"""
                SELECT SUM(product_uom_qty)
                FROM {from_clause}
                WHERE {where_clause}
            """

            self.env.cr.execute(query, where_clause_params)
            result = self.env.cr.fetchone()
            line.practical_amount = result[0] if result and result[0] else 0.0

    @api.depends("date_from", "date_to")
    def _compute_theoritical_amount(self):
        for line in self:
            total_value = line.practical_amount - line.planned_amount
            line.theoritical_amount = total_value

    def _compute_percentage(self):
        for line in self:
            if line.theoritical_amount != 0.00:
                line.percentage = float(
                    (line.practical_amount or 0.0) / line.theoritical_amount
                )
            else:
                line.percentage = 0.00

    @api.onchange("date_from", "date_to")
    def _onchange_dates(self):
        # suggesting a budget based on given dates
        domain_list = []
        if self.date_from:
            domain_list.append(
                ["|", ("date_from", "<=", self.date_from), ("date_from", "=", False)]
            )
        if self.date_to:
            domain_list.append(
                ["|", ("date_to", ">=", self.date_to), ("date_to", "=", False)]
            )
        # don't suggest if a budget is already set and verifies condition on its dates
        if domain_list and not self.purchase_crossovered_budget_id.filtered_domain(
            AND(domain_list)
        ):
            self.purchase_crossovered_budget_id = self.env[
                "purchase.crossovered.budget"
            ].search(AND(domain_list), limit=1)

    @api.onchange("purchase_crossovered_budget_id")
    def _onchange_purchase_crossovered_budget_id(self):
        if self.purchase_crossovered_budget_id:
            self.date_from = (
                self.date_from or self.purchase_crossovered_budget_id.date_from
            )
            self.date_to = self.date_to or self.purchase_crossovered_budget_id.date_to

    @api.constrains("general_budget_id", "analytic_account_id")
    def _must_have_analytical_or_budgetary_or_both(self):
        for record in self:
            if not record.analytic_account_id and not record.general_budget_id:
                raise ValidationError(
                    _(
                        "You have to enter at least a budgetary position or analytic account on a budget line."
                    )
                )

    def action_open_budget_entries(self):
        if self.analytic_account_id:
            # if there is an analytic account, then the analytic items are loaded
            action = self.env["ir.actions.act_window"]._for_xml_id(
                "analytic.account_analytic_line_action_entries"
            )
            action["domain"] = [
                ("account_id", "=", self.analytic_account_id.id),
                ("date", ">=", self.date_from),
                ("date", "<=", self.date_to),
            ]
            if self.general_budget_id:
                action["domain"] += [
                    ("general_account_id", "in", self.general_budget_id.account_ids.ids)
                ]
        else:
            # otherwise the journal entries booked on the accounts of the budgetary postition are opened
            action = self.env["ir.actions.act_window"]._for_xml_id(
                "account.action_account_moves_all_a"
            )
            action["domain"] = [
                ("account_id", "in", self.general_budget_id.account_ids.ids),
                ("date", ">=", self.date_from),
                ("date", "<=", self.date_to),
            ]
        return action

    @api.constrains("date_from", "date_to")
    def _line_dates_between_budget_dates(self):
        for line in self:
            budget_date_from = line.purchase_crossovered_budget_id.date_from
            budget_date_to = line.purchase_crossovered_budget_id.date_to
            if line.date_from:
                date_from = line.date_from
                if (budget_date_from and date_from < budget_date_from) or (
                    budget_date_to and date_from > budget_date_to
                ):
                    raise ValidationError(
                        _(
                            '"Start Date" of the budget line should be included in the Period of the budget'
                        )
                    )
            if line.date_to:
                date_to = line.date_to
                if (budget_date_from and date_to < budget_date_from) or (
                    budget_date_to and date_to > budget_date_to
                ):
                    raise ValidationError(
                        _(
                            '"End Date" of the budget line should be included in the Period of the budget'
                        )
                    )


class BudgetComponentLine(models.Model):
    _name = "budget.component.line"
    _description = "Budget Component Line"

    crossovered_budget_id = fields.Many2one(
        "purchase.crossovered.budget", string="Crossovered Budget", required=True
    )
    component_name = fields.Char(string="Nomenclature", required=True)
    quantity = fields.Float(string="Quantite Demande", required=True)
    quantity_to_purchase = fields.Float(string="Quantite a achetee", required=True)
    actual_stock = fields.Float(string="Quantite en stock", required=True)
    uom_name = fields.Char(string="UOM", required=True)
    product_crt_qty = fields.Float(string="Quantite en CRT", required=True)
    category_name = fields.Char(string="Categorie", required=True)
    cost = fields.Float(string="Cout achats", required=True, digits=(16, 3))
    practical_amount = fields.Monetary(
        string="Cout achats",
        help="Quantity actually earned/spent.",
        compute="_compute_practical_amount",
    )
    theoritical_amount = fields.Monetary(
        string="Theoretical Amount",
        help="Quantity you are expected to have earned/spent by this date.",
        precision_digits=3,
        compute="_compute_theoritical_amount",
    )
    percentage = fields.Float(
        string="Achievement",
        help="Comparison between actual and expected quantities. This measure indicates whether you are under or over budget.",
        compute="_compute_percentage",
    )
    currency_id = fields.Many2one("res.currency", readonly=True)

    @api.depends(
        "component_name",
        "crossovered_budget_id.date_from",
        "crossovered_budget_id.date_to",
    )
    def _compute_practical_amount(self):
        for line in self:
            # Récupérer les dates depuis le budget parent
            # Récupérer les dates depuis le budget parent
            date_from = line.crossovered_budget_id.date_from
            date_to = line.crossovered_budget_id.date_to

            # Vérification de base
            if not line.component_name or not date_from or not date_to:
                line.practical_amount = 0.0
                continue

            # Recherche du produit correspondant au nom
            product = self.env["product.product"].search(
                [("name", "=", line.component_name)], limit=1
            )

            if not product:
                line.practical_amount = 0.0
                continue

            # Recherche des lignes de valorisation liées à ce produit, dans la période, et issues de réceptions
            domain = [
                ("product_id", "=", product.id),
                ("stock_move_id.date", ">=", date_from),
                ("stock_move_id.date", "<=", date_to),
                ("value", ">", 0),
                ("stock_move_id.picking_type_id.code", "=", "incoming"),
            ]

            valuation_lines = self.env["stock.valuation.layer"].search(domain)
            total_value = sum(layer.value for layer in valuation_lines)

            line.practical_amount = total_value

    @api.depends(
        "component_name",
        "crossovered_budget_id.date_from",
        "crossovered_budget_id.date_to",
    )
    def _compute_theoritical_amount(self):
        for line in self:
            # Recherche du produit correspondant au nom
            product = self.env["product.product"].search(
                [("name", "=", line.component_name)], limit=1
            )
            total_value = line.quantity_to_purchase * product.standard_price
            line.theoritical_amount = total_value

    def _compute_percentage(self):
        for line in self:
            if line.theoritical_amount != 0.00:
                line.percentage = float(
                    (line.practical_amount or 0.0) / line.theoritical_amount
                )
            else:
                line.percentage = 0.00
