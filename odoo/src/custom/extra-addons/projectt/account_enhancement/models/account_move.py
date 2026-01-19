from odoo import models, api, fields
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    # sequence_option = fields.Boolean(
    #     compute="_compute_sequence_option",
    #     default=False,
    #     copy=False,
    #     store=True,
    #     index=True,
    # )

    entry_generated = fields.Boolean(string="Entry Generated",default=False)

    def action_generate_entry(self):
        for move in self:
            if move.state != 'posted':
                continue

            journal = self.env['account.journal'].search([('code', '=', 'OD')], limit=1)
            if not journal:
                raise UserError("Aucun journal trouvé avec le code 'OD'.")

            payable_account = move.partner_id.property_account_payable_id
            receivable_account = move.partner_id.property_account_receivable_id

            if not payable_account or not receivable_account:
                raise UserError("Le partenaire n’a pas de compte fournisseur/client défini.")
            if not move.ref:
                raise UserError("La référence doit être renseignée.")

            # Get maturity dates from payable lines
            payable_lines = move.line_ids.filtered(lambda l: l.account_id == payable_account)
            date_maturities = payable_lines.mapped('date_maturity')

            # pick the latest maturity date or today if none
            date_maturity = max(date_maturities) if date_maturities else False

            # set display_type only if date_maturity exists
            display_type_val = 'payment_term' if date_maturity else False

            move_vals = {
                'move_type': 'entry',
                'journal_id': journal.id,
                'entry_generated': True,
                'ref': f"RECLASSEMENT COMPTE - {move.ref}",
                'date': move.invoice_date or fields.Date.today(),
                'line_ids': [
                    (0, 0, {
                        'name': f"RECLASSEMENT COMPTE - {move.ref}",
                        'partner_id': move.partner_id.id,
                        'account_id': receivable_account.id,
                        'debit': 0.0,
                        'credit': move.amount_total,
                        'date_maturity': date_maturity,
                        'display_type': display_type_val,
                    }),
                    (0, 0, {
                        'name': f"RECLASSEMENT COMPTE - {move.ref}",
                        'partner_id': move.partner_id.id,
                        'account_id': payable_account.id,
                        'credit': 0.0,
                        'debit': move.amount_total,
                        'date_maturity': date_maturity,
                        'display_type': display_type_val,
                    }),
                ],
            }

            new_move = self.env['account.move'].create(move_vals)
            new_move.action_post()

            # Mark entry_generated if you have the field
            move.entry_generated = True

            # ----------------------
            # Reconcile payable lines
            # ----------------------
            bill_payable_lines = move.line_ids.filtered(
                lambda l: l.account_id == payable_account and l.partner_id == move.partner_id
            )
            entry_payable_lines = new_move.line_ids.filtered(
                lambda l: l.account_id == payable_account and l.partner_id == move.partner_id
            )

            lines_to_reconcile = bill_payable_lines + entry_payable_lines
            if len(lines_to_reconcile) > 1:
                lines_to_reconcile.reconcile()

            move.message_post(
                body=f"Une écriture comptable ({new_move.name}) a été créée dans le journal "
                     f"{journal.name} (code : {journal.code}) de Fournisseur → Client "
                     f"pour {move.partner_id.name}, et le compte fournisseur a été rapproché."
            )

        return True


