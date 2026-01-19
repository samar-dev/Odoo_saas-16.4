/* @odoo-module */

import { patch } from "@web/core/utils/patch";
import { MockServer } from "@web/../tests/helpers/mock_server";

patch(MockServer.prototype, "whatsapp/models/mail_message", {
    _mockMailMessageMessageFormat(ids) {
        const formattedMessages = this._super(...arguments);
        for (const formattedMessage of formattedMessages) {
            const [whatsappMessage] = this.getRecords("whatsapp.message", [
                ["mail_message_id", "=", formattedMessage.id],
            ]);
            if (whatsappMessage) {
                formattedMessage["whatsappStatus"] = whatsappMessage.state;
            }
        }
        return formattedMessages;
    },
});
