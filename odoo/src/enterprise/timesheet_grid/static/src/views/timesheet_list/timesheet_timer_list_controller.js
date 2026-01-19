/** @odoo-module */

import { useSubEnv } from "@odoo/owl";
import { ListController } from "@web/views/list/list_controller";

export class TimerTimesheetListController extends ListController {
    setup() {
        super.setup();
        useSubEnv({
            config: {
                ...this.env.config,
                disableSearchBarAutofocus: true,
            },
        });
    }
}
