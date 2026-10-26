/** @odoo-module **/
// Odoo 17 - 19: dialogs without a title are titled “Odoo”
import { Dialog } from "@web/core/dialog/dialog";
import { session } from "@web/session";

const wl = session.htp_white_label || {};
if (wl.active && wl.replace_texts && Dialog.defaultProps && Dialog.defaultProps.title === "Odoo") {
    Dialog.defaultProps = { ...Dialog.defaultProps, title: wl.name };
}
