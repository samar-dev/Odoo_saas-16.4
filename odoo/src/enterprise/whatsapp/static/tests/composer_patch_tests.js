/* @odoo-module */

import {
    afterNextRender,
    createFile,
    dragenterFiles,
    dropFiles,
    insertText,
    pasteFiles,
    start,
    startServer,
} from "@mail/../tests/helpers/test_utils";
import { Composer } from "@mail/core/common/composer";
import { patchWithCleanup } from "@web/../tests/helpers/utils";
import { file } from "web.test_utils";

const { inputFiles } = file;
const { DateTime } = luxon;

QUnit.module("composer (patch)", {
    async beforeEach() {
        // Simulate real user interactions
        patchWithCleanup(Composer.prototype, {
            isEventTrusted() {
                return true;
            },
        });
    },
});

QUnit.test("Allow only single attachment in every message", async (assert) => {
    const pyEnv = await startServer();
    const channelId = pyEnv["discuss.channel"].create({
        name: "WhatsApp 1",
        channel_type: "whatsapp",
    });
    const { openDiscuss } = await start();
    await openDiscuss(channelId);
    const [file1, file2] = [
        await createFile({
            content: "hello, world",
            contentType: "text/plain",
            name: "text.txt",
        }),
        await createFile({
            content: "hello, world",
            contentType: "text/plain",
            name: "text2.txt",
        }),
    ];
    assert.containsOnce($, ".o-mail-Composer");
    assert.containsOnce($, "button[title='Attach files']");

    await afterNextRender(() => {
        inputFiles($(".o-mail-Composer-coreMain .o_input_file")[0], [file1]);
    });
    assert.containsOnce($, ".o-mail-AttachmentCard .fa-check");
    assert.ok($("button[title='Attach files']")[0].disabled);

    await afterNextRender(() => pasteFiles($(".o-mail-Composer-input")[0], [file2]));
    assert.containsOnce($, ".o-mail-AttachmentCard .fa-check");

    await afterNextRender(() => dragenterFiles($(".o-mail-Composer-input")[0]));
    assert.containsOnce($, ".o-mail-Dropzone");
    await afterNextRender(() => dropFiles($(".o-mail-Dropzone")[0], [file2]));
    assert.containsOnce($, ".o-mail-AttachmentCard .fa-check");
});

QUnit.test("Can not add attachment after copy pasting an attachment", async (assert) => {
    const pyEnv = await startServer();
    const channelId = pyEnv["discuss.channel"].create({
        name: "WhatsApp 1",
        channel_type: "whatsapp",
    });
    const { openDiscuss } = await start();
    await openDiscuss(channelId);
    const [file1, file2] = [
        await createFile({
            content: "hello, world",
            contentType: "text/plain",
            name: "text.txt",
        }),
        await createFile({
            content: "hello, world",
            contentType: "text/plain",
            name: "text2.txt",
        }),
    ];
    await afterNextRender(() => pasteFiles($(".o-mail-Composer-input")[0], [file1]));
    assert.ok($("button[title='Attach files']")[0].disabled);

    await afterNextRender(() => pasteFiles($(".o-mail-Composer-input")[0], [file2]));
    assert.containsOnce($, ".o-mail-AttachmentCard .fa-check");

    await afterNextRender(() => dragenterFiles($(".o-mail-Composer-input")[0]));
    assert.containsOnce($, ".o-mail-Dropzone");
    await afterNextRender(() => dropFiles($(".o-mail-Dropzone")[0], [file2]));
    assert.containsOnce($, ".o-mail-AttachmentCard .fa-check");
});

QUnit.test("Can not add attachment after drag dropping an attachment", async (assert) => {
    const pyEnv = await startServer();
    const channelId = pyEnv["discuss.channel"].create({
        name: "WhatsApp 1",
        channel_type: "whatsapp",
    });
    const { openDiscuss } = await start();
    await openDiscuss(channelId);
    const [file1, file2] = [
        await createFile({
            content: "hello, world",
            contentType: "text/plain",
            name: "text.txt",
        }),
        await createFile({
            content: "hello, world",
            contentType: "text/plain",
            name: "text2.txt",
        }),
    ];
    await afterNextRender(() => dragenterFiles($(".o-mail-Composer-input")[0]));
    assert.containsOnce($, ".o-mail-Dropzone");
    await afterNextRender(() => dropFiles($(".o-mail-Dropzone")[0], [file1]));
    assert.containsOnce($, ".o-mail-AttachmentCard .fa-check");
    assert.ok($("button[title='Attach files']")[0].disabled);

    await afterNextRender(() => pasteFiles($(".o-mail-Composer-input")[0], [file2]));
    assert.containsOnce($, ".o-mail-AttachmentCard .fa-check");
});

QUnit.test(
    "Disabled composer should be enabled after message from whatsapp user",
    async (assert) => {
        const pyEnv = await startServer();
        const channelId = pyEnv["discuss.channel"].create({
            name: "WhatsApp 1",
            channel_type: "whatsapp",
            whatsapp_channel_valid_until: DateTime.utc().minus({minutes: 1}).toSQL(),
        });
        const { openDiscuss } = await start();
        await openDiscuss(channelId);
        assert.containsNone($, ".o-mail-Composer-actions");
        assert.containsNone($, "button[title='Attach files']");
        assert.containsNone($, ".o-mail-Composer-send");
        assert.ok($(".o-mail-Composer-input")[0].readOnly);

        // stimulate the notification sent after receiving a message from whatsapp user
        const [channel] = pyEnv["discuss.channel"].searchRead([["id", "=", channelId]]);
        await afterNextRender(() => {
            pyEnv["bus.bus"]._sendone(
                channel,
                "discuss.channel/whatsapp_channel_valid_until_changed",
                {
                    id: channelId,
                    whatsapp_channel_valid_until: DateTime.utc().plus({days: 1}).toSQL(),
                }
            );
        });
        assert.containsOnce($, ".o-mail-Composer-actions");
        assert.containsOnce($, "button[title='Attach files']");
        assert.containsOnce($, ".o-mail-Composer-send");
        assert.notOk($(".o-mail-Composer-input")[0].readOnly);
    }
);

QUnit.test("Allow channel commands for whatsapp channels", async (assert) => {
    const pyEnv = await startServer();
    const channelId = pyEnv["discuss.channel"].create({
        name: "WhatsApp 1",
        channel_type: "whatsapp",
    });
    const { openDiscuss } = await start();
    await openDiscuss(channelId);
    await insertText(".o-mail-Composer-input", "/");
    assert.containsOnce($, ".o-mail-NavigableList");
    assert.ok($(".o-mail-NavigableList-item").length > 0);
});
