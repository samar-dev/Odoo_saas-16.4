/** @odoo-module */

import { ThreadService } from "@mail/core/common/thread_service";
import { patch } from "@web/core/utils/patch";
import { removeFromArray } from "@mail/utils/common/arrays";
import { assignDefined } from "@mail/utils/common/misc";

patch(ThreadService.prototype, "whatsapp_thread_service", {
    canLeave(thread) {
        return thread.type !== "whatsapp" && this._super(thread);
    },

    canUnpin(thread) {
        if (thread.type === "whatsapp") {
            return this.getCounter(thread) === 0;
        }
        return this._super(thread);
    },

    getCounter(thread) {
        if (thread.type === "whatsapp") {
            return thread.message_unread_counter || thread.message_needaction_counter;
        }
        return this._super(thread);
    },

    async getMessagePostParams({thread}) {
        const params = await this._super(...arguments);

        if (thread.type === "whatsapp") {
            params.post_data.message_type = "whatsapp_message";
        }
        return params;
    },

    insert(data) {
        const thread = this._super(data);
        if (thread.type === "whatsapp") {
            if (data?.channel) {
                assignDefined(thread, data.channel, ["anonymous_name"]);
            }
        }
        return thread;
    },

    update(thread, data) {
        if (thread.type === "whatsapp") {
            assignDefined(thread, data, ["whatsapp_channel_valid_until"]);
            if (!this.store.discuss.whatsapp.threads.includes(thread.localId)) {
                this.store.discuss.whatsapp.threads.push(thread.localId);
            }
        }
        this._super(thread, data);
    },

    async openWhatsAppChannel(id, name) {
        const thread = this.insert({
            id,
            model: "discuss.channel",
            name,
            type: "whatsapp",
            channel: { avatarCacheKey: "hello" },
        });
        if (!thread.hasSelfAsMember) {
            const data = await this.orm.call("discuss.channel", "whatsapp_channel_join_and_pin", [[id]]);
            this.update(thread, data);
        } else if (!thread.is_pinned) {
            this.pin(thread);
        }
        this.sortChannels();
        this.open(thread);
    },

    remove(thread) {
        removeFromArray(this.store.discuss.whatsapp.threads, thread.localId);
        this._super(thread);
    },

    sortChannels() {
        this._super();
        // WhatsApp Channels are sorted by most recent interest date time in the sidebar.
        this.store.discuss.whatsapp.threads.sort((localId_1, localId_2) => {
            const thread1 = this.store.threads[localId_1];
            const thread2 = this.store.threads[localId_2];
            return thread2.lastInterestDateTime.ts - thread1.lastInterestDateTime.ts;
        });
    },
});
