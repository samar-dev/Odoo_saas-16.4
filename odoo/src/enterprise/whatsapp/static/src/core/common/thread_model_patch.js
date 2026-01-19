/* @odoo-module */

import { Thread } from "@mail/core/common/thread_model";
import { patch } from "@web/core/utils/patch";
import { deserializeDateTime } from "@web/core/l10n/dates";

import { toRaw } from "@odoo/owl";

patch(Thread.prototype, "whatsapp_thread_model", {
    get allowReactions() {
        return this.type === "whatsapp" ? false : this._super();
    },

    get allowSetLastSeenMessage() {
        return this.type === "whatsapp" || this._super();
    },

    get imgUrl() {
        if (this.type !== "whatsapp") {
            return this._super();
        }
        return "/mail/static/src/img/smiley/avatar.jpg";
    },

    get isChatChannel() {
        return this.type === "whatsapp" || this._super();
    },

    get isChannel() {
        return this.type === "whatsapp" || this._super();
    },

    get whatsappChannelValidUntilDatetime() {
        if (!this.whatsapp_channel_valid_until) {
            return undefined;
        }
        return toRaw(deserializeDateTime(this.whatsapp_channel_valid_until));
    },
});
