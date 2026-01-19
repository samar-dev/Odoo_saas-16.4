/** @odoo-module */

import { Message } from "@mail/core/common/message_model";
import { patch } from "@web/core/utils/patch";

patch(Message.prototype, "whatsapp_message_model", {
    get editable() {
        if (this.originThread?.type === "whatsapp") {
            return false;
        }
        return this._super();
    },
});
