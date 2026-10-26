/** @odoo-module **/
// Odoo 17 - 19: the browser tab reads “Odoo - <page>”
import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";
import { WebClient } from "@web/webclient/webclient";

const wl = session.htp_white_label || {};

patch(WebClient.prototype, {
    setup() {
        super.setup(...arguments);
        if (wl.active && wl.replace_texts) {
            const title = this.title || (this.env.services && this.env.services.title);
            if (title && title.setParts) {
                title.setParts({ zopenerp: wl.name });
            }
        }
    },
});
