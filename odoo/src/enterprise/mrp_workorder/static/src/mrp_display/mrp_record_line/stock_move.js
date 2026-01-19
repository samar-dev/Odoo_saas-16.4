/** @odoo-module */

import { Component } from "@odoo/owl";

export class StockMove extends Component {
    static props = {
        clickable: Boolean,
        displayUOM: Boolean,
        label: { optional: true, type: String },
        parent: Object,
        record: Object,
        uom: { optional: true, type: Object },
    };
    static template = "mrp_workorder.StockMove";

    setup() {
        this.fieldState = "state";
        this.isLongPressable = false;
        this.longPressed = false;
        this.resModel = this.props.record.resModel;
    }

    get cssClass() {
        let cssClass = this.isLongPressable ? "o_longpressable" : "";
        if (this.isComplete) {
            cssClass += " text-muted";
        }
        return cssClass;
    }

    get isComplete() {
        if (this.toConsumeQuantity) {
            return this.props.record.data.quantity_done >= this.toConsumeQuantity;
        }
        return Boolean(this.props.record.data.quantity_done);
    }

    get toConsumeQuantity() {
        const move = this.props.record.data;
        const parent = this.props.parent.data;
        let toConsumeQuantity = move.should_consume_qty || move.product_uom_qty;
        if (parent.product_tracking == "serial" && !parent.show_serial_mass_produce) {
            toConsumeQuantity /= this.props.parent.data.product_qty;
        }
        return toConsumeQuantity;
    }

    get quantityDone() {
        return this.props.record.data.quantity_done;
    }

    get uom() {
        if (this.displayUOM) {
            return this.props.record.data.product_uom[1];
        }
        return this.toConsumeQuantity === 1 ? this.env._t("Unit") : this.env._t("Units");
    }

    longPress() {}

    onAnimationEnd(ev) {
        if (ev.animationName === "longpress") {
            this.longPressed = true;
            this.longPress();
        }
    }

    onClick() {
        if (!this.props.clickable) {
            return;
        }
        if (this.longPressed) {
            this.longPressed = false;
            return; // Do nothing since the longpress event was already called.
        }
        this.clicked();
    }

    async clicked() {
        const action = await this.props.record.model.orm.call(
            this.resModel,
            "action_show_details",
            [this.props.record.resId]
        );
        const options = {
            onClose: () => this.reload(),
        };
        this.props.record.model.action.doAction(action, options);
    }

    async toggleQuantityDone() {
        if (!this.props.clickable) {
            return;
        } else if (!this.toConsumeQuantity) {
            return this.clicked();
        }
        const quantity = this.isComplete ? 0 : this.toConsumeQuantity;
        this.props.record.update({ quantity_done: quantity });
        this.props.record.save(); // TODO: instead of saving after each individual change, it should be better to save at some point all the changes.
        await this.reload();
    }

    async reload() {
        await this.props.parent.load();
        await this.props.record.load();
        this.props.record.model.notify();
    }

    get state() {
        return this.props.record.data[this.fieldState];
    }
}
