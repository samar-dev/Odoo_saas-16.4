from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import logging
from odoo.exceptions import UserError
from datetime import datetime


_logger = logging.getLogger(__name__)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    reconciliation_account = fields.Char(string="Compte lettrage", readonly=True)

    def action_reconciliation_wizard(self):
        return {
            "name": "Ajouter un compte de léttrage",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "reconciliation.account.wizard",
            "target": "new",
        }

    def action_cancel_reconciliation(self):
        accounts_list = self.mapped("reconciliation_account")

        # Check if all accounts are the same
        same_account = all(acc == accounts_list[0] for acc in accounts_list)

        # Extract years from the dates (convert to int for comparison)
        years = [int(d.split("-")[1]) for d in accounts_list]
        # Get company from the first record
        company = self.env.company.id
        company = self.env["res.company"].browse(company)
        is_blocked = company.is_blocked

        # If one year differs from current year
        blocked_years = set(company.blocked_year_ids.mapped("year"))

        if company.is_blocked and any(year in blocked_years for year in years):
            raise ValidationError(
                "Vous ne pouvez supprimer le rapprochement pour une année bloquée (%s)."
                % ", ".join(map(str, blocked_years))
            )

        # If all accounts are the same, reset reconciliation fields
        if same_account:
            self.reconciliation_account = None
            self.x_account_reconcile = ""
        else:
            raise ValidationError(
                "Les paiements doivent avoir le même compte de lettrage."
            )

    def unlink_zero_balance_lines(self):
        context = dict(self._context or {})

        # Check if active_ids exist in context
        if context.get("active_ids", False):
            # Browse the selected lines based on active_ids from the context
            data = self.env["account.move.line"].browse(context.get("active_ids"))

            # Filter lines based on a specific condition (if needed)
            lines_to_unlink = data.filtered(
                lambda line: line.balance == 0
            )  # Example filter: zero balance

            # Log the number of lines to be unlinked
            _logger.info(
                f"Attempting to forcefully unlink {len(lines_to_unlink)} lines."
            )

            # Forcefully unlink the filtered lines
            for item in lines_to_unlink:
                try:
                    # Check if the record exists before attempting to unlink
                    if item.exists():
                        _logger.info(
                            f"Forcefully unlinking line {item.id} (Balance: {item.balance})."
                        )
                        item.with_context(force_delete=True).sudo().unlink()
                    else:
                        _logger.warning(
                            f"Line {item.id} does not exist or has already been deleted."
                        )
                except Exception as e:
                    # Log any exceptions that occur during unlinking
                    _logger.error(f"Error unlinking line with ID {item.id}: {e}")

        return True

    def remove_move_reconcile(self):
        """Undo a reconciliation with date restriction"""

        for line in self:
            move_year = line.date.year
            company = line.company_id
            blocked_years = set(company.blocked_year_ids.mapped("year"))

            if company.is_blocked and move_year in blocked_years:
                raise ValidationError(
                    "Vous ne pouvez supprimer le rapprochement pour l'année %s car elle est bloquée."
                    % move_year
                )

        # Call original behavior
        return super().remove_move_reconcile()

