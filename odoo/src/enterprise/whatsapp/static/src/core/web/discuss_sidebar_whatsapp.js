/* @odoo-module */

import { Sidebar } from "@mail/core/web/sidebar";

import { patch } from "@web/core/utils/patch";

patch(Sidebar.prototype, "whatsapp", {
    get shouldDisplayWhatsappCategory() {
        return this.store.discuss.whatsapp.threads.some(
            (localId) => this.store.threads[localId]?.is_pinned
        );
    },
});
