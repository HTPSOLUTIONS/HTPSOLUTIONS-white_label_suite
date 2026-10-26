/** @odoo-module **/
import { Component, onWillStart, useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";
import { applyBrandToDocument } from "./htp_white_label_service";

const IMAGE_FIELDS = ["logo", "app_icon", "bot_avatar", "home_background"];

/**
 * White Label control dashboard: every branding option on one page, with a live preview.
 */
export class WhiteLabelDashboard extends Component {
    static template = "htp_white_label.Dashboard";
    static props = { ...standardActionServiceProps };

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
        this.state = useState({
            loading: true,
            saving: false,
            dirty: false,
            section: "identity",
            id: false,
            values: {},
            saved: {},
            images: {},
            newImages: {},
            companions: [],
            session: {},
            userName: "",
            busyModule: "",
        });
        this.sections = [
            { id: "identity", label: _t("Identity"), icon: "palette" },
            { id: "hide", label: _t("Texts and footers"), icon: "eye_off" },
            { id: "home", label: _t("Home screen"), icon: "home" },
            { id: "apps", label: _t("Applications"), icon: "puzzle" },
        ];
        this.toggles = [
            { name: "replace_texts", title: _t("Replace “Odoo” everywhere in the interface"),
              help: _t("Browser tab, messages, error dialogs, settings, help texts and placeholders show your brand.") },
            { name: "cleanup_user_menu", title: _t("Clean the user menu"),
              help: _t("Removes Documentation and the odoo.com account; “Help” opens your support link (or disappears).") },
            { name: "debrand_emails", title: _t("Clean the e-mails"),
              help: _t("Every e-mail sent loses “Powered by Odoo” and its links to odoo.com.") },
            { name: "hide_db_manager_link", title: _t("Hide “Manage Databases” on the login page"),
              help: _t("Also set list_db = False in the server configuration to close the database manager.") },
            { name: "hide_enterprise_upsell", title: _t("Hide Enterprise advertising"),
              help: _t("Community: the Apps menu no longer lists the paid apps and the settings marked “Enterprise” disappear.") },
            { name: "hide_documentation", title: _t("Hide the links to the Odoo documentation"),
              help: _t("The “?” and “Documentation” links of the settings and forms are hidden.") },
            { name: "replace_about", title: _t("Brand the “About” block of the settings"),
              help: _t("Shows your brand and the version instead of the Odoo copyright.") },
            { name: "debrand_bot", title: _t("Rename OdooBot"),
              help: _t("OdooBot takes the assistant name and avatar of the Identity tab.") },
        ];
        this.homeStyles = [
            { id: "default", label: _t("Standard") },
            { id: "gradient", label: _t("Gradient") },
            { id: "color", label: _t("Plain color") },
            { id: "image", label: _t("Picture") },
        ];
        this.logoPositions = [
            { id: "none", label: _t("Hidden") },
            { id: "left", label: _t("Left") },
            { id: "center", label: _t("Center") },
            { id: "right", label: _t("Right") },
        ];
        onWillStart(() => this.load());
    }

    // ------------------------------------------------------------------ data
    async load() {
        const data = await this.orm.call("white.label.config", "get_dashboard_data", []);
        this.applyData(data);
    }

    applyData(data) {
        this.state.id = data.id;
        this.state.values = { ...data.values };
        this.state.saved = { ...data.values };
        this.state.images = { ...data.images };
        this.state.newImages = {};
        this.state.companions = data.companions;
        this.state.session = data.session || {};
        this.state.userName = data.user_name;
        this.state.hasAnyLogo = data.has_any_logo;
        this.state.dirty = false;
        this.state.loading = false;
    }

    set(name, value) {
        this.state.values[name] = value;
        this.state.dirty = true;
    }

    onInput(name, ev) {
        this.set(name, ev.target.value);
    }

    onToggle(name, ev) {
        this.set(name, ev.target.checked);
    }

    onLogoSize(ev) {
        const size = parseInt(ev.target.value, 10);
        this.set("home_logo_size", Number.isNaN(size) ? 64 : Math.max(24, Math.min(size, 200)));
    }

    onColor(ev) {
        const value = ev.target.value;
        if (/^#[0-9a-fA-F]{6}$/.test(value)) {
            this.set("color", value.toLowerCase());
        } else {
            this.state.values.color = value;
        }
    }

    // ------------------------------------------------------------------ images
    imageUrl(field) {
        const fresh = this.state.newImages[field];
        if (fresh) {
            return fresh.preview;
        }
        if (fresh === false || !this.state.images[field]) {
            return "";
        }
        const stamp = this.state.session.stamp || "0";
        return `/web/image/white.label.config/${this.state.id}/${field}?unique=${stamp}`;
    }

    get iconPreview() {
        return this.imageUrl("app_icon") || `/htp_white_label/icon/128?v=${this.state.session.stamp || "0"}`;
    }

    get logoPreview() {
        return this.imageUrl("logo") || "/web/binary/company_logo";
    }

    pickImage(field) {
        const input = document.createElement("input");
        input.type = "file";
        input.accept = "image/*";
        input.addEventListener("change", () => {
            const file = input.files && input.files[0];
            if (!file) {
                return;
            }
            if (file.size > 8 * 1024 * 1024) {
                this.notification.add(_t("This picture is too large (8 MB maximum)."), { type: "danger" });
                return;
            }
            const reader = new FileReader();
            reader.addEventListener("load", () => {
                const result = reader.result;
                this.state.newImages[field] = { preview: result, data: result.split(",")[1] };
                this.state.dirty = true;
                if (field === "home_background") {
                    this.state.values.home_style = "image";
                }
            });
            reader.readAsDataURL(file);
        });
        input.click();
    }

    removeImage(field) {
        this.state.newImages[field] = false;
        this.state.dirty = true;
    }

    // ------------------------------------------------------------------ save
    async save() {
        if (!(this.state.values.brand_name || "").trim()) {
            this.notification.add(_t("Please enter your brand name."), { type: "danger" });
            this.state.section = "identity";
            return;
        }
        this.state.saving = true;
        const images = {};
        for (const field of IMAGE_FIELDS) {
            if (field in this.state.newImages) {
                const image = this.state.newImages[field];
                images[field] = image ? image.data : false;
            }
        }
        try {
            const data = await this.orm.call("white.label.config", "save_dashboard", [this.state.values, images]);
            this.applyData(data);
            applyBrandToDocument(data.session);
            const message = data.values.enabled
                ? _t("Branding saved. Reload the page to see it everywhere.")
                : _t("Saved. Your branding is off: Odoo keeps its standard look.");
            this.notification.add(message, {
                type: "success",
                buttons: [{ name: _t("Reload now"), onClick: () => window.location.reload() }],
            });
        } finally {
            this.state.saving = false;
        }
    }

    discard() {
        this.state.values = { ...this.state.saved };
        this.state.newImages = {};
        this.state.dirty = false;
    }

    // ------------------------------------------------------------------ companions
    async installCompanion(companion) {
        this.state.busyModule = companion.module;
        try {
            const action = await this.orm.call("white.label.config", "install_companion", [companion.module]);
            await this.action.doAction(action);
        } finally {
            this.state.busyModule = "";
        }
    }

    async uninstallCompanion(companion) {
        this.state.busyModule = companion.module;
        try {
            const action = await this.orm.call("white.label.config", "uninstall_companion", [companion.module]);
            await this.action.doAction(action);
        } finally {
            this.state.busyModule = "";
        }
    }

    // ------------------------------------------------------------------ preview helpers
    get brandName() {
        return (this.state.values.brand_name || "").trim() || "My Company";
    }

    get homeClass() {
        return `o_wl_home_${this.state.values.home_style || "default"}`;
    }

    get previewLogoVisible() {
        const position = this.state.values.home_logo_position || "center";
        return position !== "none" && Boolean(this.imageUrl("logo") || this.state.hasAnyLogo);
    }

    get previewLogoStyle() {
        const position = this.state.values.home_logo_position || "center";
        const size = this.state.values.home_logo_size || 64;
        const align = { left: "flex-start", center: "center", right: "flex-end" }[position] || "center";
        // the preview is about a third of a real screen
        return `height: ${Math.round(Math.max(10, size * 0.34))}px; align-self: ${align};`;
    }

    get previewStyle() {
        const color = /^#[0-9a-fA-F]{6}$/.test(this.state.values.color || "") ? this.state.values.color : "#2c3e50";
        const dark = "#" + [1, 3, 5].map((i) => Math.round(parseInt(color.slice(i, i + 2), 16) * 0.55).toString(16).padStart(2, "0")).join("");
        const background = this.imageUrl("home_background");
        return `--wl-color: ${color}; --wl-color-dark: ${dark};` + (background ? ` --wl-home-bg: url('${background}');` : "");
    }

    get botName() {
        return this.state.values.debrand_bot ? (this.state.values.bot_name || "Assistant") : "OdooBot";
    }

    get botAvatar() {
        return this.state.values.debrand_bot ? this.imageUrl("bot_avatar") : "/base/static/img/odoobot.png";
    }

    poweredByText() {
        return this.state.values.powered_by === "brand" ? `${_t("Powered by")} ${this.brandName}` : "";
    }
}

registry.category("actions").add("htp_white_label.dashboard", WhiteLabelDashboard);
