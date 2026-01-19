/** @odoo-module **/

import { Record, RelationalModel, StaticList } from "@web/views/relational_model";

export class BankRecRecord extends Record{

    /**
     * override
     * Track the changed field on lines.
     */
    async update(changes, options) {
        if(this.resModel === "bank.rec.widget.line"){
            for(const fieldName of Object.keys(changes)){
                this.model.lineIdsChangedField = fieldName;
            }
        }
        return super.update(...arguments);
    }

    /**
     * Bind an action to be called when a field on lines changed.
     * @param {Function} callback: The action to call taking the changed field as parameter.
     */
    bindActionOnLineChanged(callback){
        this.onChanges = async () => {
            const lineIdsChangedField = this.model.lineIdsChangedField;
            if(lineIdsChangedField){
                this.model.lineIdsChangedField = null;
                this.model.__onchangeInProgress = true;
                await callback(lineIdsChangedField);
                this.model.__onchangeInProgress = false;
            }
        }
    }

}

export class BankRecStaticList extends StaticList{

    setup(params, state) {
        // one2many fields are limited to 40 records by default, increase this limit while an alternative solution is found
        if (params.resModel == 'bank.rec.widget.line') {
            params.limit = 10000;
        }
        super.setup(params, state);
    }

    /**
     * override
     * Track field change for many2many fields as well like tax_ids.
     */
    applyCommands(commands) {
        if(!this.model.__onchangeInProgress && this.parentRecord && this.parentRecord.resModel === "bank.rec.widget.line"){
            this.model.lineIdsChangedField = this.field.name;
        }
        return super.applyCommands(commands);
    }

}

export class BankRecRelationalModel extends RelationalModel{

    setup(params, { action, dialog, notification, rpc, user, view, company }) {
        super.setup(...arguments);
        this.lineIdsChangedField = null;
    }

}
BankRecRelationalModel.Record = BankRecRecord;
BankRecRelationalModel.StaticList = BankRecStaticList;
