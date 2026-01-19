from odoo import fields, models, api
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.tools import float_round
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    destination_journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Destination Journal",
        domain="[('type', 'in', ('bank','cash'))]",
        check_company=True,
    )

    partner_customer_type = fields.Char(
        store=True,
        readonly=True
    )

    original_money = fields.Monetary(
        string='Montant en devise',
        currency_field='original_currency',
        copy=False,
    )
    original_currency = fields.Many2one(
        'res.currency',
        string='Devise',
        copy=False,
    )
    is_company_currency = fields.Boolean(
        string="Is Company Currency",
        compute="_compute_is_company_currency",
        store=False
    )

    @api.depends('currency_id', 'company_id.currency_id')
    def _compute_is_company_currency(self):
        for rec in self:
            rec.is_company_currency = rec.currency_id == rec.company_id.currency_id

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

    def action_post(self):
        # Poster le paiement normalement
        res = super(AccountPayment, self).action_post()

        for payment in self:
            partner = payment.partner_id
            payment.partner_customer_type = partner.x_customer_type if partner else None
            # Skip payments that are not from import suppliers
            if payment.partner_customer_type != 'import_supplier':
                continue

            # Skip payments with no original currency or zero original amount
            if not payment.original_currency or payment.original_money == 0.0:
                continue

            # Préparer toutes les lignes
            lines_vals = []
            for line in payment.move_id.line_ids:
                vals = {'currency_id': payment.original_currency.id}

                # amount_currency et forcer debit/credit selon la ligne
                if line.debit > 0:
                    vals['amount_currency'] = abs(payment.original_money)
                    vals['debit'] = payment.amount
                    vals['credit'] = 0.0
                elif line.credit > 0:
                    vals['amount_currency'] = -abs(payment.original_money)
                    vals['debit'] = 0.0
                    vals['credit'] = payment.amount
                else:
                    # ligne à zéro
                    vals['amount_currency'] = 0.0
                    vals['debit'] = 0.0
                    vals['credit'] = 0.0

                lines_vals.append((line, vals))

            # Mettre à jour toutes les lignes à la fin
            for line, vals in lines_vals:
                line.with_context(skip_account_move_synchronization=True).write(vals)

        return res

    @api.model
    def create(self, vals):
        # Récupérer le partenaire
        res = super(AccountPayment, self).create(vals)
        for record in res:
            partner = record.partner_id
            record.partner_customer_type = partner.x_customer_type if partner else None

            # Vérifications uniquement si le type de client est import/export
            if record.partner_customer_type in ['import_supplier'] and record.currency_id == record.company_id.currency_id:
                if 'original_money' not in vals or vals.get('original_money', 0.0) == 0.0:
                    raise ValidationError("Le montant d’origine ne peut pas être égal à 0.")
                if not vals.get('original_currency'):
                    raise ValidationError("La devise d’origine est obligatoire pour ce type de partenaire.")

        return res

    @api.onchange('partner_id', )
    def _check_original_fields_required(self):
        for record in self:
            record.partner_customer_type = record.partner_id.x_customer_type
