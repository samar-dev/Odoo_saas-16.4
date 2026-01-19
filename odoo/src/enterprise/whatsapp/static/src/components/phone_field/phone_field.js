/** @odoo-module **/

import { _lt } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { PhoneField, phoneField, formPhoneField } from "@web/views/fields/phone/phone_field";
import { SendWhatsAppButton } from "../whatsapp_button/whatsapp_button.js";

patch(PhoneField, "whatsapp_PhoneField", {
    components: {
        ...PhoneField.components,
        SendWhatsAppButton,
    },
    defaultProps: {
        ...PhoneField.defaultProps,
        enableWhatsAppButton: true,
    },
    props: {
        ...PhoneField.props,
        enableWhatsAppButton: { type: Boolean, optional: true },
    },
});

const patchDescr = {
    extractProps({ options }) {
        const props = this._super(...arguments);
        props.enableWhatsAppButton = options.enable_whatsapp;
        return props;
    },
    supportedOptions: [
        ...(phoneField.supportedOptions ? phoneField.supportedOptions : []),
        {
            label: _lt("Enable WhatsApp"),
            name: "enable_whatsapp",
            type: "boolean",
            default: true,
        },
    ],
};

patch(phoneField, "whatsapp_phoneField", patchDescr);
patch(formPhoneField, "whatsapp_formPhoneField", patchDescr);
