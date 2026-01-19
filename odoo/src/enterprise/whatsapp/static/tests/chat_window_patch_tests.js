/* @odoo-module */

import { click, start, startServer } from "@mail/../tests/helpers/test_utils";

QUnit.module("messaging menu (patch)");

QUnit.test("WhatsApp channel chat windows should have thread icon", async (assert) => {
    const pyEnv = await startServer();
    pyEnv["discuss.channel"].create({
        name: "WhatsApp 1",
        channel_type: "whatsapp",
    });
    await start();
    await click(".o_menu_systray i[aria-label='Messages']");
    await click(".o-mail-NotificationItem");
    assert.containsOnce($, ".o-mail-ChatWindow-header .o-mail-ThreadIcon");
});
