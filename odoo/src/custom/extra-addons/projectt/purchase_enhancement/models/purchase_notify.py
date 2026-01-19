from odoo import models, api
from datetime import date, timedelta

class PurchaseNotify(models.Model):
    _name = 'purchase.notify'
    _description = 'Notifications Achats'

    @api.model
    def notify_overdue(self):
        purchase_group = self.env.ref("purchase.group_purchase_manager")
        user_ids = purchase_group.users

        if not user_ids:
            return self._base_display_notification(
                type="warning",
                message="Impossible de trouver un responsable des achats",
                sticky=False,
            )

        today = date.today()
        seven_days_ago = today - timedelta(days=7)

        quotations = self.env['purchase.order'].search([
            ('state', '=', 'draft'),
            ('date_order', '<=', seven_days_ago)
        ])

        orders = self.env['purchase.order'].search([
            ('state', '=', 'purchase'),
            ('date_order', '<=', seven_days_ago),
            ('picking_ids.state', '!=', 'done')
        ])

        # Commandes avec date_planned après date_approve filtrées en Python
        all_confirmed_orders = self.env['purchase.order'].search([('state', '=', 'purchase'),('picking_ids.state', '!=', 'done')])
        delayed_orders = all_confirmed_orders.filtered(
            lambda o: o.date_planned and o.date_approve and o.date_planned > o.date_approve
        )

        message = "<p>Bonjour, vous avez des éléments en retard ou planifiés après approbation :</p><ul>"

        for q in quotations:
            message += f'<li>Devis : <a href="#" data-oe-model="purchase.order" data-oe-id="{q.id}">{q.name}</a> (en brouillon)</li>'
        for o in orders:
            message += f'<li>Commande : <a href="#" data-oe-model="purchase.order" data-oe-id="{o.id}">{o.name}</a> (non livrée)</li>'
        for o in delayed_orders:
            message += f'<li>Commande : <a href="#" data-oe-model="purchase.order" data-oe-id="{o.id}">{o.name}</a> (date prévue après approbation)</li>'

        message += "</ul>"

        if quotations or orders or delayed_orders:
            channel_name = "Notifications Achats"
            self._base_send_a_message(user_ids, channel_name, message)
            return self._base_display_notification(
                title=channel_name,
                type="success",
                message=f"{len(quotations) + len(orders) + len(delayed_orders)} notifications envoyées aux responsables des achats",
                sticky=False,
            )
        else:
            return self._base_display_notification(
                type="info",
                message="Aucun élément en retard ou planifié après approbation",
                sticky=False,
            )
