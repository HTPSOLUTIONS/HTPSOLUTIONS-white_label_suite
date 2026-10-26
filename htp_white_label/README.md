# White Label Branding (Odoo 17, 18, 19, 20)

Make your Odoo look like your company, from one dashboard with a live preview.

**Nothing changes when the module is installed.** Open **Settings > White Label**, choose your settings, switch on
**Apply my branding** and save. Switching it off brings back the standard Odoo look (OdooBot, Apps menu, installed-app
name and website favicons included).
Publisher: HIGHTECH PRO. License: OPL-1.

## What it changes

| Area | Without White Label | With White Label |
|---|---|---|
| Browser tab | “Odoo” title and favicon | your brand name and icon (uploaded, or drawn from your initial and color) |
| Installed app (PWA) | “Odoo” name and icons | your name and icons |
| Interface texts | “Odoo Server Error”, “Odoo needs…”, help texts, placeholders | every “Odoo” word becomes your brand (links to odoo.com are kept) |
| Dialog titles | “Odoo” | your brand |
| “Powered by Odoo” | login, portal, website, surveys, e-mails | hidden, or “Powered by your brand” with your website |
| User menu | Documentation, Help (odoo.com), My Odoo.com account | Documentation and odoo.com account removed, Help opens your support link or disappears |
| Login page | “Manage Databases” link | hidden (also set `list_db = False` on the server) |
| Settings | “About”: product name and links; “Enterprise” upsell (Community); documentation links | your brand and version (Odoo's copyright line is kept); upsell removed; documentation links hidden |
| Apps menu (Community) | paid Enterprise apps with “Upgrade” | only the apps you can install |
| Discuss | OdooBot | your assistant name and avatar |
| Top bar and main buttons | Odoo purple | your brand color, text color adapted for contrast |
| Home | first application (Community) | a full-screen dashboard of your applications, on your background, with your logo, a greeting and a search bar |
| Logo on the home screen | — | left, centered or right, with the height you choose (Community dashboard and Enterprise home screen) |

Every option can be switched off on its own in the dashboard (**Settings > White Label**).

## Only the applications you use

The base module depends on `web`, `mail` and `base_setup` only. Each application has its own small companion module,
listed in the dashboard (**Applications** tab) with an “Enable” button when the application is installed.
Enabling a companion never installs the application.

| Module | Depends on | Changes |
|---|---|---|
| `htp_white_label` | web, mail, base_setup | everything above |
| `htp_white_label_portal` | portal | “Powered by [Odoo logo]” of the portal documents (quotations, invoices…) |
| `htp_white_label_website` | website | `<meta name="generator">`, default favicon of the websites, `/website/info` |
| `htp_white_label_pos` | point_of_sale | POS logo, receipt “Powered by Odoo”, customer display logo |
| `htp_white_label_livechat` | im_livechat | “Website Live Chat Powered by Odoo” support page |
| `htp_white_label_enterprise` | web_enterprise | Enterprise home screen and login background, logo above the apps (position and size), menu search bar |

## Works alongside other debranding modules

Modules that already remove “Powered by Odoo” (login page, portal, POS receipt…) can stay installed:

- White Label hides Odoo's elements instead of deleting them, so a module installed after it still finds what it changes.
- When a module installed before White Label already removed an element, White Label skips that change
  (a line in the server log) instead of breaking the page. This applies to White Label's own views only.

## What it does not do

- It keeps Odoo's copyright notice (Settings > About) and the license files of the source code.
- It does not touch the Enterprise subscription mechanisms (expiration warnings, registration, “My Subscription”
  for administrators). Debranding is about what your users see, not about the license.
- The database manager page (`/web/database/manager`) runs without a database, so no installed module can change it:
  close it with `list_db = False` in the server configuration.
- Content written by people (website pages, product descriptions, e-mail templates you wrote) is never modified.
- Odoo 17 customer facing display (the old HTML one) keeps its “Powered by” logo.

## Uninstall

Uninstalling restores OdooBot (name and picture), the Apps menu filter, the installed-app name and the website favicons
that White Label had set.

## Technical notes

- The interface texts are rebranded on the server: web client translations (`ir.http`), view architectures and field
  labels (`_get_view` / `fields_get`), outgoing e-mails (`mail.mail`).
- Template inheritance never depends on translatable text, so it works in every language.
- Each module has automated tests (`tests/`).

---

## En français

**White Label** donne à votre Odoo l'image de votre entreprise : nom, logo, icône de l'onglet, couleurs, écran d'accueil
(logo à gauche, au centre ou à droite, à la taille voulue) et e-mails. Rien ne change à l'installation : tout se règle dans
**Paramètres > White Label**, avec un aperçu en direct, puis s'active avec l'interrupteur “Apply my branding”.
Chaque application (site web, point de vente, portail, chat, écran d'accueil Enterprise) a son petit module complémentaire :
vous n'activez que ce que vous utilisez, sans jamais installer d'application en plus.
