/** @odoo-module **/

import { patch, unpatch } from "@web/core/utils/patch";
import { Wysiwyg } from '@web_editor/js/wysiwyg/wysiwyg';
import { insert, createPeers, removePeers } from '@web_editor/../tests/test_wysiwyg_collaboration';

/**
 * Returns a cleaned html value as it would be saved in the database,
 * notably to avoid paragraph placeholder when it contains the selection, ...
 *
 * @param {PeerTest} peer @see test_wysiwyg_collaboration.js
 * @returns {String} html value with selection represented as `[]`
 */
function getCleanedValue(peer) {
    peer.wysiwyg.odooEditor.cleanForSave();
    return peer.getValue();
}

QUnit.module("Knowledge - Collaboration", (hooks) => {
    hooks.beforeEach(() => {
        patch(Wysiwyg, "knowledge_collaborative_wysiwyg_static", {
            activeCollaborationChannelNames: {
                has: () => false,
                add: () => {},
                delete: () => {},
            },
        });
        patch(Wysiwyg.prototype, "knowledge_collaborative_wysiwyg_prototype", {
            setup() {
                const result = this._super(...arguments);
                this.busService = {
                    addEventListener: () => {},
                    removeEventListener: () => {},
                    addChannel: () => {},
                    deleteChannel: () => {},
                };
                return result;
            },
        });
    });
    hooks.afterEach(() => {
        unpatch(Wysiwyg, "knowledge_collaborative_wysiwyg_static");
        unpatch(Wysiwyg.prototype, "knowledge_collaborative_wysiwyg_prototype");
    });
    QUnit.test('Check that collaborative external append is correctly inserted', async function (assert) {
        let notifyNewBehaviorCount = 0;
        patch(Wysiwyg.prototype, "knowledge_collaborative_wysiwyg_notifyNewBehavior", {
            /**
             * Replace the original method to only test a basic insertion in
             * the editor, because this test only cares about how many times
             * this method is called (and if it was called at the right time).
             */
            _notifyNewBehavior(element, restoreSelection, insert) {
                restoreSelection();
                insert(element);
                notifyNewBehaviorCount++;
            }
        });
        const pool = await createPeers(['p1', 'p2']);
        const peers = pool.peers;

        await peers.p1.startEditor();
        await peers.p2.startEditor();

        await peers.p1.focus();
        await peers.p2.focus();

        await peers.p1.makeStep(insert('s1'));

        const behaviorEl = peers.p2.document.createElement('DIV');
        const paragraph = peers.p2.document.createElement('P');
        paragraph.append(peers.p2.document.createTextNode("b1"));
        behaviorEl.append(paragraph);
        behaviorEl.setAttribute("name", "b1");
        peers.p2.wysiwyg.appendBehaviorBlueprint(behaviorEl);

        // Synchronize history of p2 with the one from p1
        await peers.p1.openDataChannel(peers.p2);

        assert.equal(getCleanedValue(peers.p1), `<p>as1[]</p><div name="b1"><p>b1</p></div><p><br></p>`);
        assert.equal(getCleanedValue(peers.p2), `<p>as1</p><div name="b1"><p>b1</p></div><p><br>[]</p>`);
        // The method should have been called twice:
        // - once for the insertion outside of the collaboration.
        // - a second time when the editable of p2 is resynchronized with the
        //   one from p1, which was the first connected user.
        assert.equal(notifyNewBehaviorCount, 2);

        removePeers(peers);
        unpatch(Wysiwyg.prototype, "knowledge_collaborative_wysiwyg_notifyNewBehavior");
    });
});
