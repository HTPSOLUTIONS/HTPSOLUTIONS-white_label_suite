/** @odoo-module **/
import { Component, onMounted, onWillStart, useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";
import { applyBrandToDocument } from "./htp_white_label_service";

/**
 * Branded home dashboard: full-screen grid of the user's applications with the brand logo and background.
 */
export class WhiteLabelHome extends Component {
    static template = "htp_white_label.HomeDashboard";
    static props = { ...standardActionServiceProps };

    setup() {
        this.menu = useService("menu");
        this.ui = useService("ui");
        this.wl = session.htp_white_label || {};
        this.state = useState({ search: "", now: new Date() });
        onWillStart(() => applyBrandToDocument(this.wl));
        onMounted(() => {
            const input = document.querySelector(".o_wl_home_search input");
            if (input && !this.ui.isSmall) {
                input.focus();
            }
        });
    }

    get apps() {
        const term = this.state.search.trim().toLowerCase();
        const apps = this.menu.getApps();
        return term ? apps.filter((app) => app.name.toLowerCase().includes(term)) : apps;
    }

    get backgroundClass() {
        return `o_wl_home_${this.wl.home_style || "gradient"}`;
    }

    get greeting() {
        const hour = this.state.now.getHours();
        const name = (this.wl.user_name || "").split(" ")[0];
        let text;
        if (hour < 5 || hour >= 18) {
            text = _t("Good evening");
        } else if (hour < 12) {
            text = _t("Good morning");
        } else {
            text = _t("Good afternoon");
        }
        return name ? `${text}, ${name}` : text;
    }

    get today() {
        return this.state.now.toLocaleDateString(undefined, { weekday: "long", day: "numeric", month: "long" });
    }

    iconSrc(app) {
        const data = app.webIconData;
        if (!data) {
            return "";
        }
        if (data.startsWith("data:image") || data.startsWith("/")) {
            return data;
        }
        const prefix = data.startsWith("P") ? "data:image/svg+xml;base64," : "data:image/png;base64,";
        return prefix + data.replace(/\s/g, "");
    }

    initials(app) {
        return (app.name || "?").trim().slice(0, 1).toUpperCase();
    }

    onSearch(ev) {
        this.state.search = ev.target.value;
    }

    onSearchKeydown(ev) {
        if (ev.key === "Enter" && this.apps.length) {
            this.open(this.apps[0]);
        }
    }

    open(app) {
        this.menu.selectMenu(app);
    }
}

registry.category("actions").add("htp_white_label.home_dashboard", WhiteLabelHome);
