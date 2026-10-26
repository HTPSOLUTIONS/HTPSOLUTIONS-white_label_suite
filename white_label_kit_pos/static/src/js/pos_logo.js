/** @odoo-module **/
import { OdooLogo } from "@point_of_sale/app/generic_components/odoo_logo/odoo_logo";
import { session } from "@web/session";

// Only when the branding is on: the Odoo logo of the Point of Sale and of the customer display becomes the brand logo.
// These pages have their own layout: the class and the logo variable used by the styles are set here.
const wl = session.white_label_kit || {};
if (wl.active) {
    OdooLogo.template = "white_label_kit_pos.Logo";
    const mark = () => {
        document.body.classList.add("o_wl_active");
        if (wl.logo_url) {
            document.documentElement.style.setProperty("--wl-logo", `url("${wl.logo_url}")`);
        }
    };
    if (document.body) {
        mark();
    } else {
        document.addEventListener("DOMContentLoaded", mark);
    }
}
