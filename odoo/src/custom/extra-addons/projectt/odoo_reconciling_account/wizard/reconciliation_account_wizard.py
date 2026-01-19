import random
import string

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class ReconciliationWizard(models.TransientModel):
    _name = "reconciliation.account.wizard"
    _description = "Wizard reconciliation account"

    reconciliation_account = fields.Char(string="Compte lettrage")

    def action_confirm(self):
        active_ids = self._context.get("active_ids")
        # Fetch the account.move.line records
        line_ids = self.env["account.move.line"].browse(active_ids)

        # Separate bank accounts from others
        accounts = line_ids.filtered(lambda line: not line.account_id.code.startswith("53"))
        accounts_bank = line_ids.filtered(lambda line: line.account_id.code.startswith("53"))

        # Validate selection
        if accounts and not accounts_bank:
            raise ValidationError(
                "Les paiements doivent être sur un compte bancaire pour être rapprochés"
            )
        elif accounts and accounts_bank:
            raise ValidationError(
                "Les paiements ne doivent pas avoir des comptes différents, veuillez vérifier votre choix avant de procéder au rapprochement"
            )
        else:
            for line in line_ids:
                payment_ids = self.env["account.payment"].search(
                    [("id", "=", line.payment_id.id)]
                )
                if payment_ids:
                    payment_ids[0].x_skip_account_move_sync = True
                line.reconciliation_account = self.reconciliation_account


class AccountReconcileWizard(models.TransientModel):
    """This wizard is used to reconcile selected account.move.line."""

    _inherit = "account.reconcile.wizard"

    forced_reconcile = fields.Boolean(string="Forced Reconcile", default=False)

    def reconcile(self):
        res = super(AccountReconcileWizard, self).reconcile()
        if self.allow_partials:
            letter_r = random.choice(string.ascii_lowercase)
        else:
            letter_r = random.choice(string.ascii_uppercase)
        for record in res:
            record.x_account_reconcile = letter_r

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def reconcile(self):
        res = super(AccountMoveLine, self).reconcile()

        # Process per INVOICE line (not per payment)
        invoice_lines = self.filtered(
            lambda l: l.move_id.move_type in ('out_invoice', 'in_invoice')
            and l.account_id.reconcile
        )
        for invoice_line in invoice_lines:
            # FULL or PARTIAL?
            if invoice_line.full_reconcile_id:
                # FULL → UPPERCASE
                letter = random.choice(string.ascii_uppercase)

                lines = self.env['account.move.line'].search([
                    ('full_reconcile_id', '=', invoice_line.full_reconcile_id.id)
                ])
            else:
                # PARTIAL → lowercase
                letter = random.choice(string.ascii_lowercase)

                # Invoice + ALL matched payment lines
                partials = (
                    invoice_line.matched_debit_ids |
                    invoice_line.matched_credit_ids
                )
                lines = invoice_line | partials.debit_move_id | partials.credit_move_id
            lines.write({'x_account_reconcile': letter})

        return res




