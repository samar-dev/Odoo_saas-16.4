from odoo import api, exceptions, models, fields
from odoo.tests.common import Form
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    refund_tax_stamp = fields.Boolean(string="Avec Timbre Fiscal", default=True)

    def _check_product_accounts(self):
        """
        No need to check for tax stamp product accounts
        if the partner is not eligible or currency is not TND,
        or we have no invoice lines
        :return: -1 if the move doesn't need to check for product at all
        """
        self.ensure_one()
        if (
            self.partner_id.is_taxable
            and self.currency_id.name == "TND"
            and self.invoice_line_ids
        ):
            # tax stamp product
            product_id = self.env["product.product"].search(
                [
                    ("is_tax_stamp", "=", True),
                    ("company_id", "in", [False, self.env.company.id]),
                ],
                limit=1,
            )
            if not (
                product_id.property_account_income_id
                and product_id.property_account_expense_id
            ):
                raise exceptions.ValidationError(
                    "Le produit de timbre fiscal doit avoir un compte de revenus et de "
                    "dépenses"
                )
            return product_id
        return -1

    def _add_tax_stamp(self):
        """
        Check if we got a tax stamp product in invoice_line_ids.
        If we got one when we don't need itn we remove it.
        If we have none when we need it, we add it.
        :return: None
        """
        self.ensure_one()
        product_id = self._check_product_accounts()
        # no need to execute the process
        if product_id == -1:
            return
        product_accounts = [*product_id._get_product_accounts().values()]
        if self.is_invoice(include_receipts=True):
            # check if we already have the tax stamp in the journal items
            tax_stamp_line = self.invoice_line_ids.filtered(
                lambda line: line.account_id in product_accounts
                and line.product_id.is_tax_stamp
            )
            tax_stamp_line_index = (
                tax_stamp_line
                and list(self.invoice_line_ids).index(tax_stamp_line)
                or -1
            )
            if (
                self.move_type in ("out_refund", "in_refund")
                and not self.refund_tax_stamp
            ):
                # in case it is a refund
                # odoo will automatically pass the same lines of the invoice
                # in that case we simply remove it
                # or in a case the user is playing with the credit note
                # by checking and unchecking the refund_tax_stamp field
                if tax_stamp_line and tax_stamp_line_index != -1:
                    with Form(self.with_context(changed_by_adding_tax=True)) as move:
                        move.invoice_line_ids.remove(tax_stamp_line_index)
                return
            # if tax stamp line is not found, partner is eligible for taxes
            # and the currency is Tunisian Dinars, and we have at least a single product
            if (
                not tax_stamp_line
                and self.partner_id.is_taxable
                and self.currency_id.name == "TND"
                and self.invoice_line_ids
            ):
                with Form(self.with_context(changed_by_adding_tax=True)) as move:
                    with move.invoice_line_ids.new() as line:
                        line.product_id = product_id
            elif (
                tax_stamp_line
                and tax_stamp_line_index != -1
                and (not self.partner_id.is_taxable or self.currency_id.name != "TND")
            ):
                with Form(self.with_context(changed_by_adding_tax=True)) as move:
                    move.invoice_line_ids.remove(tax_stamp_line_index)

    @api.model_create_multi
    def create(self, vals_list):
        res = super(AccountMove, self).create(vals_list)
        for move in res:
            move._add_tax_stamp()
        return res

    def write(self, vals):
        res = super(AccountMove, self).write(vals)
        for move in self:
            # to prevent recursionError,
            # calling write method again by adding a tax stamp line
            if not self._context.get("changed_by_adding_tax"):
                move._add_tax_stamp()
        return res

    
