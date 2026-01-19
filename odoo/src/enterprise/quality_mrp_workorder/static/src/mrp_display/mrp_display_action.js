/** @odoo-module */

import { patch } from 'web.utils';
import { MrpDisplayAction } from "@mrp_workorder/mrp_display/mrp_display_action";

patch(MrpDisplayAction.prototype, 'quality_mrp_workorder', {
    get fieldsStructure() {
        let res = this._super();
        res['mrp.production'].push('quality_check_todo');
        return res;
    }
})