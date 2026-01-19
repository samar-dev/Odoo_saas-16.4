/** @odoo-module */

import { Thread } from "@mail/core/common/thread";
import { patch } from "@web/core/utils/patch";

patch(Thread.prototype, "whatsapp_thread", {
    isSquashed(msg, prevMsg) {
        if (msg.whatsappStatus === "error") {
            return false;
        }
        return this._super(msg, prevMsg);
    },
});
