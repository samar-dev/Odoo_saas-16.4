/** @odoo-module */

import { patch } from 'web.utils';
import { MrpDisplayRecord } from "@mrp_workorder/mrp_display/mrp_display_record";

patch(MrpDisplayRecord.prototype, 'quality_mrp_workorder', {
    async validate() {
        const { resModel, resId } = this.props.record;
        if (resModel === "mrp.production") {
            if (this.record.quality_check_todo) {
                const action = await this.model.orm.call(resModel, 'check_quality', [resId]);
                return this._doAction(action);
            }
        }
        return this._super();
    },

    _shouldValidateProduction(){
        return this._super() && !this.props.production.data.quality_check_todo;
    },

    _productionDisplayDoneButton() {
        return this.qualityChecks.every((qc) => ["fail", "pass"].includes(qc.data.quality_state) || !qc.data.workorder_id);
    },
})