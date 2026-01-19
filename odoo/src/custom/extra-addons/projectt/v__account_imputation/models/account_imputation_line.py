from odoo import _, fields, models
from odoo.exceptions import UserError


class AccountImputationLine(models.Model):
    _name = "account.imputation.line"
    _rec_name = "move_id"

    account_imputation_id = fields.Many2one(comodel_name="account.imputation")
    company_id = fields.Many2one(
        string=_("Company"),
        comodel_name="res.company",
        default=lambda self: self.env.company,
        required=True,
    )
    date = fields.Date(string=_("Date"), required=True)
    move_id = fields.Many2one(
        string=_("Journal Entry"), comodel_name="account.move", required=True
    )
    move_line_id = fields.Many2one(
        string=_("Journal Item"), comodel_name="account.move.line", required=True
    )
    matching_number = fields.Char(string=_("Matching #"))
    partner_id = fields.Many2one(string=_("Partner"), comodel_name="res.partner")
    credit = fields.Float(string=_("Credit"))
    debit = fields.Float(string=_("Debit"))
    account_id = fields.Many2one(
        string=_("Old account"), comodel_name="account.account"
    )
    new_account_id = fields.Many2one(
        string=_("New account"), comodel_name="account.account"
    )
    journal_id = fields.Many2one(string=_("Journal"), comodel_name="account.journal")
    excluded = fields.Boolean(default=False)

    def action_set_excluded(self):
        if self.account_imputation_id.state in ("done", "canceled"):
            raise UserError(_("You cannot exclude lines at this stage"))
        self.excluded = True

    def action_set_included(self):
        if self.account_imputation_id.state in ("done", "canceled"):
            raise UserError(_("You cannot include lines at this stage"))
        self.excluded = False
