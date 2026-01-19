/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { Messaging } from "@mail/core/common/messaging_service";
import { createLocalId } from "@mail/utils/common/misc";

patch(Messaging.prototype, "whatsapp_messaging_service", {
    handleNotification(notifications) {
        this._super(...arguments);

        for (const notif of notifications) {
            switch (notif.type) {
                case "discuss.channel/whatsapp_channel_valid_until_changed":
                    {
                        const { id, whatsapp_channel_valid_until } = notif.payload;
                        const channel = this.store.threads[createLocalId("discuss.channel", id)];
                        if (channel) {
                            this.threadService.update(channel, { whatsapp_channel_valid_until });
                        }
                    }
                    break;
                case "mail.record/insert":
                    {
                        const { "res.users.settings": settings } = notif.payload;
                        if (settings) {
                            this.store.discuss.whatsapp.isOpen =
                                settings.is_discuss_sidebar_category_whatsapp_open ??
                                this.store.discuss.whatsapp.isOpen;
                        }
                    }
            }
        }
    },

    initMessagingCallback(data) {
        this._super(data);
        if (data.current_user_settings?.is_discuss_sidebar_category_whatsapp_open) {
            this.store.discuss.whatsapp.isOpen = true;
        }
    },

    _handleNotificationLastInterestDtChanged(notif) {
        this._super(notif);
        const channel = this.store.threads[createLocalId("discuss.channel", notif.payload.id)];
        if (channel?.type === "whatsapp") {
            this.threadService.sortChannels();
        }
    },

    _handleNotificationRecordInsert(notif) {
        this._super(notif);
        const { "res.users.settings": settings } = notif.payload;
        if (settings) {
            this.store.discuss.whatsapp.isOpen =
                settings.is_discuss_sidebar_category_whatsapp_open ??
                this.store.discuss.whatsapp.isOpen;
        }
    },
});
