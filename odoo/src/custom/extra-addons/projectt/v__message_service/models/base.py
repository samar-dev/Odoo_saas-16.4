from odoo import fields, models, SUPERUSER_ID
from odoo.addons.base.models.res_users import Users
from odoo.addons.mail.models.mail_activity import MailActivity
from markupsafe import Markup


class Base(models.AbstractModel):
    _inherit = "base"

    def _base_create_activity(
        self,
        obj: models.Model,
        title: str,
        message: str,
        user_id: Users,
        due_date: fields.Date,
    ) -> MailActivity:
        """
        Create an activity and assign it to the user_id
        :param obj: Odoo record
        :param title: Summary of the activity
        :param message: Note of the activity
        :param user_id: Assigned to whom
        :param due_date: Deadline of the activity
        :return: the acitivity created
        """
        activity_data = {
            "res_id": obj.id,
            "res_model_id": self.env["ir.model"]._get(obj._name).id,
            "activity_type_id": self.env.ref("mail.mail_activity_data_todo").id,
            "summary": title,
            "note": message,
            "user_id": user_id.id,
            "date_deadline": due_date,
        }
        activity_id = self.env["mail.activity"].sudo().create(activity_data)
        return activity_id

    def _base_send_a_message(
        self, user_ids: Users, channel_name: str, message: str
    ) -> None:
        """
        Create a chat message and open the chat window automatically
        the user that sends the message need to be available also as a recepient
        :param user_ids: users related to the channel
        :param channel_name: name of the chat
        :param message: message to send can be html
        :return: None
        """
        # Create a new mail.channel object
        mail_channel = self.env["discuss.channel"]
        channel = mail_channel.search([("name", "=", channel_name)])
        if not channel:
            channel = self.env["discuss.channel"].create(
                {
                    "name": channel_name,
                    "channel_partner_ids": [
                        (4, user.partner_id.id) for user in user_ids
                    ],
                    "channel_type": "channel",
                }
            )
        # in case the member of the existing channel has been changed
        # we should always keep it updated
        partner_ids = user_ids.mapped("partner_id")
        channel.channel_partner_ids = partner_ids
        channel.sudo().message_post(
            body=Markup(message),
            message_type="comment",
            subtype_id=self.env.ref("mail.mt_comment").id,
            author_id=self.env["res.users"].browse(SUPERUSER_ID).partner_id.id,
        )

    @staticmethod
    def _base_display_notification(
        title: str, type: str, message: str, sticky: bool = False
    ) -> dict:
        """
        issues with returning this notification from python won't reload
        and refresh the view, so the user needs to manually
        reload the page to see the changes
        for that reason we chain our action with another type of action
        :param title: title of notification
        :param type: types: success,warning,danger,info
        :param message: body text of notification
        :param sticky: True/False will display for few seconds if false
        :return:
        """
        notification = {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": title,
                "type": type,
                "message": message,
                "sticky": sticky,
                "next": {
                    "type": "ir.actions.act_window_close",
                },
            },
        }
        return notification
