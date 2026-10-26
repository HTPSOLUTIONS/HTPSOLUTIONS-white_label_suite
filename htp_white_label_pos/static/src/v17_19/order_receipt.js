/** @odoo-module **/
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";

patch(OrderReceipt.prototype, {
    get wlPoweredBy() {
        const wl = session.htp_white_label || {};
        if (!wl.active) {
            return "Powered by Odoo";
        }
        return wl.powered_by === "brand" ? `Powered by ${wl.name}` : "";
    },
});
