from odoo import fields, models, api,_
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from datetime import datetime
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange("currency_id")
    def check_rate_date(self):
        for record in self:
            value = record.currency_id
            print(value)
            # Assuming currency_id is an instance of the currency model
            if (
                value and value.name != "TND" and record.company_id.have_currency
            ):  # Check currency code
                future_rates = value.rate_ids.filtered(lambda r: r.name >= date.today())
                print(len(future_rates))
                if not future_rates:
                    raise UserError(
                        f"Aucun taux futur trouvé pour la devise {value.name} le {date.today()}."
                    )
                elif len(future_rates) > 1:
                    raise UserError(
                        f"Tu ne peux pas fixer une devise à une date ultérieure à  {date.today()}."
                    )

    @api.model
    def create(self, vals):
        move_date = vals.get("date")
        company = self.env["res.company"].browse(
            vals.get("company_id")
        ) or self.env.company

        if move_date and company.blocked_year_ids:
            move_date = fields.Date.from_string(move_date)
            blocked_years = set(company.blocked_year_ids.mapped("year"))

            if move_date.year in blocked_years:
                raise ValidationError(
                    "Vous ne pouvez pas créer des écritures pour l'année %s car elle est bloquée."
                    % move_date.year
                )

        return super(AccountMove, self).create(vals)

    def write(self, vals):
        for move in self:
            # Use new date if provided, otherwise existing one
            move_date = vals.get("date") or move.date
            company = move.company_id

            if move_date and company.is_blocked and company.blocked_year_ids:
                move_date = fields.Date.from_string(move_date)
                blocked_years = set(company.blocked_year_ids.mapped("year"))

                if move_date.year in blocked_years:
                    raise ValidationError(
                        "Vous ne pouvez pas modifier une écriture pour l'année %s car elle est bloquée."
                        % move_date.year
                    )

        return super(AccountMove, self).write(vals)

    def button_draft(self):
        for move in self:
            if move.date and move.company_id.blocked_year_ids:
                blocked_years = set(move.company_id.blocked_year_ids.mapped("year"))

                if move.date.year in blocked_years:
                    raise ValidationError(
                        "Vous ne pouvez pas remettre en brouillon une écriture pour l'année %s car elle est bloquée."
                        % move.date.year
                    )

        return super().button_draft()

    def action_post(self):
        for move in self:
            # --- New numbering check (only for journal VTEL) ---
            allowed_user_ids = [2, 31]

            if move.journal_id.code == "VTEL" and move.move_type == "out_invoice":
                invoice_date = move.invoice_date or date.today()
                year_prefix = invoice_date.strftime('%y')
                expected_prefix = f"FV{year_prefix}"

                # Search for existing posted invoices of the same year
                same_year_invoices = self.search([
                    ("id", "!=", move.id),
                    ("journal_id.code", "=", "VTEL"),
                    ("move_type", "=", "out_invoice"),
                    ("state", "=", "posted"),
                    ("name", "like", expected_prefix + "%"),
                ])

                if self.env.uid not in allowed_user_ids and not same_year_invoices:

                    # FV + YY + 6 digits = 10 chars
                    if len(move.name) != 10 or not move.name.startswith("FV2"):
                        raise UserError(_("Format invalide. Exemple attendu : FV26000001"))

                    # Check prefix (FV + year)
                    if not move.name.startswith(expected_prefix):
                        raise UserError(
                            _(f"Le numéro de facture ne correspond pas à l'année. Préfixe attendu : {expected_prefix}")
                        )

                    sequence_str = move.name[-6:]
                    if not sequence_str.isdigit():
                        raise UserError(_("La séquence doit être numérique à 6 chiffres."))

                    sequence = int(sequence_str)

                    # Must start at 000001 for the first invoice of the year
                    if sequence != 1:
                        raise UserError(_("La première facture de l'année doit commencer à 000001."))

            return super().action_post()
