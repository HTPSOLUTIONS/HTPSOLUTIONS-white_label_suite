/** @odoo-module **/
import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";
import { standardWidgetProps } from "@web/views/widgets/standard_widget_props";
import { Setting } from "@web/views/form/setting/setting";
import { WebClient } from "@web/webclient/webclient";

const wl = session.white_label_kit || {};

function shade(hex, ratio) {
    const value = (hex || "#2c3e50").replace("#", "");
    const rgb = [0, 2, 4].map((i) => parseInt(value.slice(i, i + 2), 16) || 0);
    const out = rgb.map((c) => Math.max(0, Math.min(255, Math.round(c * ratio))));
    return "#" + out.map((c) => c.toString(16).padStart(2, "0")).join("");
}

export function applyBrandToDocument(data = wl) {
    const root = document.documentElement;
    const body = document.body;
    if (!data.active) {
        // branding off: standard Odoo look
        for (const name of ["--wl-color", "--wl-color-dark", "--wl-on-color", "--wl-home-bg", "--wl-home-logo-size"]) {
            root.style.removeProperty(name);
        }
        if (body) {
            for (const cls of [...body.classList]) {
                if (cls.startsWith("o_wl_")) {
                    body.classList.remove(cls);
                }
            }
        }
        return;
    }
    root.style.setProperty("--wl-color", data.color || "#2c3e50");
    root.style.setProperty("--wl-color-dark", shade(data.color, 0.55));
    if (data.on_color) {
        root.style.setProperty("--wl-on-color", data.on_color);
    }
    if (data.home_background_url) {
        root.style.setProperty("--wl-home-bg", `url("${data.home_background_url}")`);
    } else {
        root.style.removeProperty("--wl-home-bg");
    }
    if (data.home_logo_size) {
        root.style.setProperty("--wl-home-logo-size", `${data.home_logo_size}px`);
    }
    if (body) {
        body.classList.add("o_wl_active");
        body.classList.toggle("o_wl_hide_docs", Boolean(data.hide_documentation));
        body.classList.toggle("o_wl_color_navbar", Boolean(data.color_navbar));
        for (const style of ["default", "color", "gradient", "image"]) {
            body.classList.toggle(`o_wl_home_style_${style}`, data.home_style === style);
        }
        body.classList.toggle("o_wl_has_home_logo", Boolean(data.home_logo));
        for (const position of ["left", "center", "right"]) {
            body.classList.toggle(`o_wl_home_logo_${position}`, data.home_logo === position);
        }
    }
}

// --------------------------------------------------------------------------- service
registry.category("services").add("white_label_kit", {
    start() {
        applyBrandToDocument(wl);
        return { data: wl, apply: applyBrandToDocument };
    },
});

// --------------------------------------------------------------------------- user menu
if (wl.active && wl.cleanup_user_menu) {
    const items = registry.category("user_menuitems");
    for (const key of ["documentation", "odoo_account"]) {
        if (items.contains(key)) {
            items.remove(key);
        }
    }
    if (!wl.support_url && items.contains("support")) {
        items.remove("support");
    }
}

// --------------------------------------------------------------------------- “About” section of the settings
export class WhiteLabelAbout extends Component {
    static template = "white_label_kit.About";
    static components = { Setting };
    static props = { ...standardWidgetProps };

    setup() {
        this.wl = wl;
        this.serverVersion = session.server_version;
    }
}

if (wl.active && wl.replace_about) {
    registry.category("view_widgets").add("res_config_edition", { component: WhiteLabelAbout }, { force: true });
}

// --------------------------------------------------------------------------- landing page: branded home dashboard
export function homeDashboardEnabled() {
    return Boolean(wl.active && wl.home_dashboard && !wl.is_enterprise);
}

patch(WebClient.prototype, {
    _loadDefaultApp() {
        if (homeDashboardEnabled()) {
            return this.actionService.doAction("white_label_kit.action_home_dashboard", { clearBreadcrumbs: true });
        }
        return super._loadDefaultApp(...arguments);
    },
});

export class WhiteLabelSystrayHome extends Component {
    static template = "white_label_kit.SystrayHome";

    setup() {
        this.action = useService("action");
    }

    openHome() {
        this.action.doAction("white_label_kit.action_home_dashboard", { clearBreadcrumbs: true });
    }
}

if (homeDashboardEnabled()) {
    registry.category("systray").add("white_label_kit.home", { Component: WhiteLabelSystrayHome }, { sequence: 1000 });
}
