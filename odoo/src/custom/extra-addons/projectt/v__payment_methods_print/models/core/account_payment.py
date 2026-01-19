from odoo import exceptions, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def print_customized_document(self) -> dict:
        """
        Each payment_method_line has a specific paperformat and specific qweb view
        we change the default action report to use the desired paperformat and qweb view

        :return: ir_actions_report
        """
        self.ensure_one()
        action_id = self.env.ref(
            "v__payment_methods_print.print_customized_document_action"
        )
        payment_method_id = self.payment_method_id
        payment_method_line_id = self.payment_method_line_id
        paperformat_id = payment_method_line_id.report_paperformat_id
        report_key = payment_method_line_id.qweb_template_id.key

        if not payment_method_id.is_printable:
            raise exceptions.ValidationError(
                "Vous n'êtes pas autorisé à imprimer pour ce type de paiement"
            )

        # payment method line must have a defined qweb view and paperformat
        elif not all((report_key, paperformat_id)):
            raise exceptions.ValidationError(
                "La vue Qweb ou le format papier n'est pas défini"
                " pour le moyen de paiement sélectionné"
            )

        # replace old report key from the action and replace it
        # we have multiple reports depending on the journal and payment method
        action_id.write(
            {
                "report_file": report_key,
                "report_name": report_key,
                "paperformat_id": paperformat_id,
            }
        )
        return action_id.report_action(self)
