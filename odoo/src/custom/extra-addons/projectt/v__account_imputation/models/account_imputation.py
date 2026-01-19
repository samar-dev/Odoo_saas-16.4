from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression


class AccountImputation(models.Model):
    _name = "account.imputation"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Imputation"

    name = fields.Char(
        string=_("Number"),
        required=True,
        default="/",
        readonly=True,
        states={"draft": [("readonly", False)]},
        copy=False,
    )
    company_id = fields.Many2one(
        string=_("Company"),
        comodel_name="res.company",
        default=lambda self: self.env.company,
        required=True,
    )
    active = fields.Boolean(default=True)
    date_from = fields.Date(
        string=_("Start Date"),
        default=lambda self: fields.Date.today().replace(month=1, day=1),
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    date_to = fields.Date(
        string=_("End Date"),
        default=lambda self: fields.Date.today().replace(month=12, day=31),
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    journal_ids = fields.Many2many(
        string=_("Journals"),
        comodel_name="account.journal",
        readonly=True,
        states={"draft": [("readonly", False)]},
        domain="[('company_id', 'in', (company_id, False))]",
    )
    minimum_amount = fields.Float(
        string=_("Minimum amount"),
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    maximum_amount = fields.Float(
        string=_("Maximum amount"),
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    balance_type = fields.Selection(
        string="Balance",
        selection=[("credit", _("Credit")), ("debit", _("Debit")), ("both", _("Both"))],
        required=True,
        default="both",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    old_account_id = fields.Many2one(
        string=_("Old account"),
        comodel_name="account.account",
        required=True,
        tracking=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    new_account_id = fields.Many2one(
        string=_("New account"),
        comodel_name="account.account",
        required=True,
        tracking=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    state = fields.Selection(
        selection=[
            ("draft", _("Draft")),
            ("pending", _("Pending")),
            ("done", _("Done")),
            ("canceled", _("Canceled")),
        ],
        tracking=True,
        default="draft",
    )
    account_imputation_line_ids = fields.One2many(
        comodel_name="account.imputation.line", inverse_name="account_imputation_id"
    )
    account_imputation_line_count = fields.Integer(
        compute="_compute_account_imputation_line_count"
    )
    include_reconciled = fields.Boolean(
        string=_("Include reconciled"),
        default=False,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    forced = fields.Boolean(default=False)

    reference = fields.Char(
        string=_("Reference"),
    )

    libelle = fields.Char(
        string=_("Libelle"),
    )

    _sql_constraints = [
        (
            "check_amount_range",
            "check(minimum_amount >= 0 and maximum_amount >= 0)",
            _("Amount can't be negative"),
        )
    ]

    @api.depends("account_imputation_line_ids")
    def _compute_account_imputation_line_count(self):
        for record in self:
            record.account_imputation_line_count = len(
                record.account_imputation_line_ids
            )

    def action_reset_to_draft(self):
        self.ensure_one()
        self.state = "draft"
        self.account_imputation_line_ids.unlink()

    def action_start_imputation(self):
        self.ensure_one()
        self.state = "pending"
        domain = []
        filters = {
            "date_from": ("date", ">="),
            "date_to": ("date", "<="),
            "journal_ids": ("journal_id", "in"),
            "reference": ("ref", "like"),
            "libelle": ("name", "like"),
        }
        for name, (field, operator) in filters.items():
            value = self[name]
            if value:
                if isinstance(value, models.Model):
                    value = f"%{value}%"
                domain.append((field, operator, value))

        if self.balance_type == "credit":
            domain.append(("debit", "=", 0))
            credit_domain = self._get_amount_domain("credit")
            domain.extend(credit_domain)

        elif self.balance_type == "debit":
            domain.append(("credit", "=", 0))
            debit_domain = self._get_amount_domain("debit")
            domain.extend(debit_domain)
        else:
            credit_domain = self._get_amount_domain("credit")
            debit_domain = self._get_amount_domain("debit")
            domain.extend(credit_domain)
            domain = expression.OR(
                [domain, debit_domain],
            )

        # retrieve all move_lines depends on the domain specified above
        # also we filter to get only the desired account
        # NOTE: we get all lines reconciled or not
        move_line_ids = (
            self.env["account.move.line"]
            .search(domain)
            .filtered(lambda line: line.account_id == self.old_account_id)
        )
        # if include reconciled not checked we need to remove the reconciled lines
        if not self.include_reconciled:
            move_line_ids = move_line_ids.filtered(
                lambda line: not line.matching_number
            )
        to_create = move_line_ids.mapped(
            lambda line: {
                "account_imputation_id": self.id,
                "date": line.date,
                "move_id": line.move_id.id,
                "move_line_id": line.id,
                "partner_id": line.partner_id.id,
                "credit": line.credit,
                "debit": line.debit,
                "account_id": line.account_id.id,
                "new_account_id": self.new_account_id.id,
                "journal_id": line.journal_id.id,
                "matching_number": line.matching_number,
            }
        )
        self.account_imputation_line_ids.create(to_create)

    def _get_amount_domain(self, balance_type):
        new_domain = []
        if self.minimum_amount:
            new_domain.append((balance_type, ">=", self.minimum_amount))
        if self.maximum_amount:
            new_domain.append((balance_type, "<=", self.maximum_amount))
            new_domain.append((balance_type, "!=", 0))
        return new_domain

    def action_open_imputation_line(self):
        self.ensure_one()
        action = {
            "name": _("Account Imputation"),
            "view_mode": "tree,form",
            "res_model": "account.imputation.line",
            "type": "ir.actions.act_window",
            "context": {"create": False, "edit": False, "delete": False},
            "domain": [("account_imputation_id", "=", self.id)],
            "target": "self",
        }
        return action

    def action_open_real_move_lines(self):
        self.ensure_one()
        action = {
            "name": _("Journal Items"),
            "view_mode": "tree",
            "res_model": "account.move.line",
            "type": "ir.actions.act_window",
            "context": {"create": False, "edit": False, "delete": False},
            "domain": [("id", "in", self.account_imputation_line_ids.move_line_id.ids)],
            "target": "self",
        }
        return action

    def action_confirm(self):
        self.ensure_one()
        move_line_ids = self.account_imputation_line_ids.filtered_domain(
            [("excluded", "=", False)]
        ).move_line_id
        if not move_line_ids:
            raise ValidationError(_("No lines selected to be altered!"))
        if self._context.get("force_confirm"):
            self.forced = True
            ids = tuple(move_line_ids.ids)
            if len(ids) == 1:
                ids = f"({move_line_ids.id})"
            self.env.cr.execute(
                "update account_move_line set account_id=%s where id in %s"
                % (self.new_account_id.id, ids),
            )
        else:
            move_line_ids.sudo().account_id = self.new_account_id
        self.state = "done"

    def action_rollback(self):
        self.ensure_one()
        move_line_ids = self.account_imputation_line_ids.filtered_domain(
            [("excluded", "=", False)]
        ).move_line_id
        if self.forced:
            ids = tuple(move_line_ids.ids)
            if len(ids) == 1:
                ids = f"({move_line_ids.id})"
            self.env.cr.execute(
                "update account_move_line set account_id=%s where id in %s"
                % (self.old_account_id.id, ids),
            )
        else:
            move_line_ids.sudo().account_id = self.old_account_id
        self.state = "canceled"

    @api.constrains("date_from", "date_to")
    def _check_date_range(self):
        self.ensure_one()
        if self.date_from and self.date_to:
            if self.date_from > self.date_to:
                raise ValidationError(
                    _("The end date must be greater than the start date")
                )

    @api.constrains("minimum_amount", "maximum_amount")
    def _check_amount_range(self):
        self.ensure_one()
        if self.minimum_amount > self.maximum_amount and self.maximum_amount != 0:
            raise ValidationError(
                _("The minimum amount must be less than the maximum amount")
            )

    @api.model_create_multi
    def create(self, vals_list):
        res = super(AccountImputation, self).create(vals_list)
        for record in res.filtered_domain([("name", "=", "/")]):
            record.name = self.env["ir.sequence"].next_by_code(
                "account.imputation.code"
            )
        return res

    @api.ondelete(at_uninstall=False)
    def _on_delete_draft(self):
        for record in self:
            if record.state != "draft":
                raise UserError(
                    _("You can't delete this document because it is not in draft state")
                )
