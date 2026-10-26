/** @odoo-module **/
// Odoo 17 - 19: dialogs without a title are titled “Odoo”
import { Dialog } from "@web/core/dialog/dialog";
import { session } from "@web/session";

const wl = session.white_label_kit || {};
if (wl.active && wl.replace_texts && Dialog.defaultProps && Dialog.defaultProps.title === "Odoo") {
    Dialog.defaultProps = { ...Dialog.defaultProps, title: wl.name };
}
