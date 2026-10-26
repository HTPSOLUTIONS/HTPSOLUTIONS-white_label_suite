import hashlib
import io
import logging
import re

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from .compat import clear_all_caches, image_bytes, ormcache, set_config_parameter

_logger = logging.getLogger(__name__)

HEX_COLOR_RE = re.compile(r'^#[0-9a-fA-F]{6}$')
DEFAULT_COLOR = '#2c3e50'

# Optional companion modules: technical name -> (application they debrand, label shown in the dashboard)
COMPANIONS = [
    ('white_label_kit_portal', 'portal', 'Customer portal'),
    ('white_label_kit_website', 'website', 'Website'),
    ('white_label_kit_pos', 'point_of_sale', 'Point of Sale'),
    ('white_label_kit_livechat', 'im_livechat', 'Live Chat'),
    ('white_label_kit_enterprise', 'web_enterprise', 'Enterprise home screen'),
]


class WhiteLabelConfig(models.Model):
    _name = 'white.label.config'
    _description = 'White Label settings'

    name = fields.Char(default='White Label', readonly=True)
    enabled = fields.Boolean(
        string='Apply my branding', default=False,
        help='Off: Odoo keeps its standard look. Installing the module changes nothing until this is switched on.')
    brand_name = fields.Char(string='Brand name', required=True,
                             default=lambda self: self.env.company.name or 'My Company')
    brand_website = fields.Char(string='Brand website', help='Used instead of odoo.com in footers and e-mails.')
    support_url = fields.Char(string='Help / support link', help='Target of the “Help” entry of the user menu. '
                                                                 'Leave empty to remove the entry.')
    logo = fields.Image(string='Logo', max_width=1024, max_height=1024,
                        help='Wide logo: login page, home screen and e-mails. Defaults to the company logo.')
    app_icon = fields.Image(string='App icon', max_width=512, max_height=512,
                            help='Square icon: browser tab (favicon), installed app, phone home screen. '
                                 'When empty, an icon is drawn with the initial of the brand.')
    color = fields.Char(string='Brand color', default=DEFAULT_COLOR, help='Hexadecimal color, e.g. #2c3e50')
    color_navbar = fields.Boolean(string='Apply the color to the interface', default=False,
                                  help='The top bar, the main buttons and the switches take the brand color.')
    bot_name = fields.Char(string='Assistant name', default='Assistant', help='Replaces “OdooBot” in Discuss.')
    bot_avatar = fields.Image(string='Assistant avatar', max_width=512, max_height=512)

    powered_by = fields.Selection([
        ('hide', 'Hide it'),
        ('brand', 'Powered by my brand'),
    ], string='“Powered by Odoo”', default='hide', required=True)
    replace_texts = fields.Boolean(string='Replace “Odoo” in the interface', default=True,
                                   help='Titles, messages, error dialogs, settings, browser tab…')
    cleanup_user_menu = fields.Boolean(
        string='Clean the user menu', default=True,
        help='Removes Documentation, the odoo.com account and points Help to your support link.')
    hide_db_manager_link = fields.Boolean(string='Hide “Manage Databases”', default=True)
    debrand_emails = fields.Boolean(string='Clean outgoing e-mails', default=True,
                                    help='Removes “Powered by Odoo” and the links to odoo.com from every e-mail sent.')
    hide_enterprise_upsell = fields.Boolean(string='Hide Enterprise advertising', default=True,
                                            help='Community: hides the paid apps of the Apps menu and the settings '
                                                 'marked “Enterprise”. No effect on an Enterprise database.')
    hide_documentation = fields.Boolean(string='Hide links to the Odoo documentation', default=True)
    replace_about = fields.Boolean(string='Brand the “About” section of the settings', default=True)
    debrand_bot = fields.Boolean(string='Rename OdooBot', default=True)

    home_style = fields.Selection([
        ('default', 'Standard'),
        ('color', 'Brand color'),
        ('gradient', 'Gradient'),
        ('image', 'Image'),
    ], string='Home screen background', default='default', required=True)
    home_background = fields.Image(string='Background image', max_width=2560, max_height=2560)
    home_dashboard = fields.Boolean(
        string='Branded home dashboard', default=True,
        help='Opens a full-screen grid of your applications, with your logo and background, when you log in.')
    home_greeting = fields.Boolean(string='Greet the user on the home dashboard', default=True)
    home_logo_position = fields.Selection([
        ('none', 'Hidden'),
        ('left', 'Left'),
        ('center', 'Center'),
        ('right', 'Right'),
    ], string='Logo on the home screen', default='center', required=True,
        help='Shown above the applications when you have a logo (yours or the company logo).')
    home_logo_size = fields.Integer(string='Logo height (pixels)', default=64)

    # values saved before the module touched them, restored on uninstall
    original_bot_name = fields.Char(readonly=True)
    original_bot_image = fields.Binary(readonly=True, attachment=True)
    original_apps_domain = fields.Char(readonly=True)
    original_web_app_name = fields.Char(readonly=True)  # False: never changed by White Label

    # ------------------------------------------------------------------ access
    @api.model
    def _get_config(self):
        config = self.sudo().search([], limit=1)
        if not config:
            config = self.sudo().create({})
        return config

    @api.model
    def action_open_dashboard(self):
        return {'type': 'ir.actions.client', 'tag': 'white_label_kit.dashboard', 'name': _('White Label')}

    # ------------------------------------------------------------------ cached public data
    @api.model
    @ormcache()
    def _brand_data(self):
        """Plain values used by every request (session info, templates, e-mails); cached until a change."""
        config = self.sudo().search([], limit=1)
        installed = set(self.env['ir.module.module'].sudo().search([('state', '=', 'installed')]).mapped('name'))
        if not config:
            return {'active': False, 'is_enterprise': 'web_enterprise' in installed}
        stamp = str(int(config.write_date.timestamp())) if config.write_date else '0'
        if not config.enabled:
            # branding off: every template, route and script keeps the standard Odoo look
            return {'active': False, 'is_enterprise': 'web_enterprise' in installed, 'stamp': stamp}
        color = config.color if config.color and HEX_COLOR_RE.match(config.color) else DEFAULT_COLOR
        color_dark = '#' + ''.join('%02x' % int(int(color[i:i + 2], 16) * 0.55) for i in (1, 3, 5))
        red, green, blue = (int(color[i:i + 2], 16) / 255 for i in (1, 3, 5))
        luminance = 0.2126 * red + 0.7152 * green + 0.0722 * blue
        on_color = '#1f2937' if luminance > 0.62 else '#ffffff'
        css_vars = ('--wl-color: %s; --wl-color-dark: %s; --wl-on-color: %s; '
                    '--wl-logo: url("/white_label_kit/logo?v=%s");') % (color, color_dark, on_color, stamp)
        if config.home_background:
            css_vars += ' --wl-home-bg: url("/white_label_kit/home_background?v=%s");' % stamp
        logo_size = max(24, min(int(config.home_logo_size or 64), 200))
        css_vars += ' --wl-home-logo-size: %dpx;' % logo_size
        has_logo = bool(config.logo) or self._company_has_logo()
        home_logo = config.home_logo_position if has_logo and config.home_logo_position != 'none' else ''
        body_class = 'o_wl_active o_wl_home_style_%s' % (config.home_style or 'default')
        if config.color_navbar:
            body_class += ' o_wl_color_navbar'
        if home_logo:
            body_class += ' o_wl_has_home_logo o_wl_home_logo_%s' % home_logo
        return {
            'active': True,
            'name': config.brand_name or 'My Company',
            'website': (config.brand_website or '').strip(),
            'support_url': (config.support_url or '').strip(),
            'color': color,
            'color_dark': color_dark,
            'on_color': on_color,
            'color_navbar': config.color_navbar,
            'css_vars': css_vars,
            'bot_name': config.bot_name or '',
            'powered_by': config.powered_by,
            'replace_texts': config.replace_texts,
            'cleanup_user_menu': config.cleanup_user_menu,
            'hide_db_manager_link': config.hide_db_manager_link,
            'debrand_emails': config.debrand_emails,
            'hide_enterprise_upsell': config.hide_enterprise_upsell,
            'hide_documentation': config.hide_documentation,
            'replace_about': config.replace_about,
            'debrand_bot': config.debrand_bot,
            'home_style': config.home_style,
            'has_home_background': bool(config.home_background),
            'home_dashboard': config.home_dashboard,
            'home_greeting': config.home_greeting,
            'has_logo': bool(config.logo),
            'has_any_logo': has_logo,
            'home_logo': home_logo,
            'home_logo_size': logo_size,
            'body_class': body_class,
            'has_app_icon': bool(config.app_icon),
            'stamp': stamp,
            'is_enterprise': 'web_enterprise' in installed,
        }

    @api.model
    def _company_has_logo(self):
        """True when the main company has a logo of its own (not the “Your logo” placeholder)."""
        company = self.env.ref('base.main_company', raise_if_not_found=False) or self.env.company
        if not company or not company.logo:
            return False
        try:
            placeholder = company._get_logo()
        except Exception:  # noqa: BLE001 - no default logo on this version: trust the field
            return True
        return hashlib.sha1(image_bytes(company.logo)).digest() != hashlib.sha1(image_bytes(placeholder)).digest()

    @api.model
    def _session_data(self):
        """Subset sent to the browser (session info): no secret, only what the interface needs."""
        data = dict(self._brand_data())
        if not data.get('active'):
            return data
        stamp = data['stamp']
        data.update({
            'icon_url': '/white_label_kit/icon/192?v=%s' % stamp,
            'favicon_url': '/white_label_kit/icon/64?v=%s' % stamp,
            'logo_url': '/white_label_kit/logo?v=%s' % stamp,
            'home_background_url': (
                '/white_label_kit/home_background?v=%s' % stamp if data['has_home_background'] else ''),
        })
        return data

    # ------------------------------------------------------------------ CRUD
    @api.constrains('home_logo_size')
    def _check_home_logo_size(self):
        for config in self:
            if config.home_logo_size and not 24 <= config.home_logo_size <= 200:
                raise UserError(_('The logo height must be between 24 and 200 pixels.'))

    @api.constrains('color')
    def _check_color(self):
        for config in self:
            if config.color and not HEX_COLOR_RE.match(config.color):
                raise UserError(_('The brand color must look like #2c3e50.'))

    @api.model_create_multi
    def create(self, vals_list):
        if self.sudo().search_count([]):
            raise UserError(_('The White Label settings already exist.'))
        configs = super().create(vals_list)
        configs._apply()
        return configs

    def write(self, vals):
        if vals.get('color'):
            vals['color'] = vals['color'].strip().lower()
        result = super().write(vals)
        self._apply()
        return result

    def unlink(self):
        raise UserError(_('Uninstall the White Label module to restore the Odoo branding.'))

    # ------------------------------------------------------------------ effects outside the module
    def _apply(self):
        """Propagate the settings to the records they control, then reset the caches."""
        self.ensure_one()
        self = self.sudo()
        if self.enabled:
            self._apply_bot()
            self._apply_apps_menu()
            self._apply_web_app_name()
        else:
            self._restore_bot()
            self._restore_apps_menu()
            self._restore_web_app_name()
        self._white_label_apply_extra()
        clear_all_caches(self.env)

    def _white_label_apply_extra(self):
        """Hook for the companion modules (website favicon…): apply when ``self.enabled``, restore otherwise."""
        return True

    def _apply_bot(self):
        partner = self.env.ref('base.partner_root', raise_if_not_found=False)
        if not partner:
            return
        if not self.original_bot_name:
            super(WhiteLabelConfig, self).write({
                'original_bot_name': partner.name or 'OdooBot',
                'original_bot_image': partner.image_1920 or False,
            })
        if self.debrand_bot:
            vals = {}
            if self.bot_name and partner.name != self.bot_name:
                vals['name'] = self.bot_name
            if self.bot_avatar:
                vals['image_1920'] = self.bot_avatar
            if vals:
                partner.write(vals)
        else:
            self._restore_bot()

    def _restore_bot(self):
        partner = self.env.ref('base.partner_root', raise_if_not_found=False)
        if partner and self.original_bot_name and partner.name != self.original_bot_name:
            vals = {'name': self.original_bot_name}
            if self.original_bot_image:
                vals['image_1920'] = self.original_bot_image
            partner.write(vals)

    def _apply_apps_menu(self):
        action = self.env.ref('base.open_module_tree', raise_if_not_found=False)
        if not action:
            return
        if self.original_apps_domain is False or self.original_apps_domain is None:
            super(WhiteLabelConfig, self).write({'original_apps_domain': action.domain or '[]'})
        is_enterprise = bool(self.env['ir.module.module'].search_count(
            [('name', '=', 'web_enterprise'), ('state', '=', 'installed')]))
        if self.hide_enterprise_upsell and not is_enterprise:
            wanted = "[('to_buy', '=', False)]"
        else:
            wanted = self.original_apps_domain or False
        if wanted == '[]':
            wanted = False
        if (action.domain or False) != wanted:
            action.write({'domain': wanted})

    def _restore_apps_menu(self):
        action = self.env.ref('base.open_module_tree', raise_if_not_found=False)
        if action and action.domain == "[('to_buy', '=', False)]":
            original = self.original_apps_domain
            action.write({'domain': original if original and original != '[]' else False})

    def _apply_web_app_name(self):
        """Odoo 18+: name of the installed app (PWA)."""
        if 'web_app_name' not in self.env['res.config.settings']._fields:
            return
        param = self.env['ir.config_parameter'].sudo().search([('key', '=', 'web.web_app_name')], limit=1)
        if self.original_web_app_name is False:
            super(WhiteLabelConfig, self).write({'original_web_app_name': param.value or ''})
        if (param.value or '') != self.brand_name:
            set_config_parameter(self.env, 'web.web_app_name', self.brand_name)

    def _restore_web_app_name(self):
        if self.original_web_app_name is False or 'web_app_name' not in self.env['res.config.settings']._fields:
            return
        params = self.env['ir.config_parameter'].sudo().search([('key', '=', 'web.web_app_name')])
        if params.filtered(lambda p: p.value == self.brand_name):
            if self.original_web_app_name:
                set_config_parameter(self.env, 'web.web_app_name', self.original_web_app_name)
            else:
                params.unlink()
        super(WhiteLabelConfig, self).write({'original_web_app_name': False})

    # ------------------------------------------------------------------ images
    def _icon_png(self, size):
        """PNG bytes of the app icon at the requested size (drawn from the brand initial when no icon is set)."""
        self.ensure_one()
        size = max(16, min(int(size or 64), 512))
        from PIL import Image, ImageDraw, ImageFont
        if self.app_icon:
            image = Image.open(io.BytesIO(image_bytes(self.app_icon))).convert('RGBA')
            image.thumbnail((size, size), Image.LANCZOS)
            canvas = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            canvas.paste(image, ((size - image.width) // 2, (size - image.height) // 2), image)
        else:
            canvas = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(canvas)
            color = self.color if self.color and HEX_COLOR_RE.match(self.color) else DEFAULT_COLOR
            radius = max(2, size // 5)
            draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=color)
            letter = (self.brand_name or '?').strip()[:1].upper() or '?'
            font = None
            for candidate in ('DejaVuSans-Bold.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                              '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'):
                try:
                    font = ImageFont.truetype(candidate, int(size * 0.62))
                    break
                except OSError:
                    continue
            if font is None:
                font = ImageFont.load_default()
            box = draw.textbbox((0, 0), letter, font=font)
            x = (size - (box[2] - box[0])) / 2 - box[0]
            y = (size - (box[3] - box[1])) / 2 - box[1]
            draw.text((x, y), letter, font=font, fill='#ffffff')
        output = io.BytesIO()
        canvas.save(output, format='PNG')
        return output.getvalue()

    # ------------------------------------------------------------------ dashboard
    @api.model
    def get_dashboard_data(self):
        if not self.env.user.has_group('base.group_system'):
            raise UserError(_('Only administrators can change the branding.'))
        config = self._get_config()
        modules = self.env['ir.module.module'].sudo().search(
            [('name', 'in', [c[0] for c in COMPANIONS] + [c[1] for c in COMPANIONS])])
        state = {m.name: m.state for m in modules}
        companions = []
        for technical, target, label in COMPANIONS:
            if technical not in state:
                continue  # companion not available in the addons path
            companions.append({
                'module': technical,
                'target': target,
                'label': _(label),
                'target_installed': state.get(target) == 'installed',
                'installed': state.get(technical) == 'installed',
                'state': state.get(technical),
            })
        values = config.read([
            'enabled', 'brand_name', 'brand_website', 'support_url', 'color', 'color_navbar', 'bot_name', 'powered_by',
            'replace_texts', 'cleanup_user_menu', 'hide_db_manager_link', 'debrand_emails', 'hide_enterprise_upsell',
            'hide_documentation', 'replace_about', 'debrand_bot', 'home_style', 'home_dashboard', 'home_greeting',
            'home_logo_position', 'home_logo_size',
        ])[0]
        return {
            'id': config.id,
            'values': values,
            'images': {
                'logo': bool(config.logo), 'app_icon': bool(config.app_icon),
                'bot_avatar': bool(config.bot_avatar), 'home_background': bool(config.home_background),
            },
            'session': self._session_data(),
            'has_any_logo': bool(config.logo) or self._company_has_logo(),
            'is_enterprise': self._brand_data().get('is_enterprise'),
            'companions': companions,
            'company_name': self.env.company.name,
            'user_name': self.env.user.name,
        }

    @api.model
    def save_dashboard(self, values, images=None):
        """Save the dashboard form. ``images`` maps a field to a base64 string, or False to remove it."""
        if not self.env.user.has_group('base.group_system'):
            raise UserError(_('Only administrators can change the branding.'))
        allowed = {
            'enabled', 'brand_name', 'brand_website', 'support_url', 'color', 'color_navbar', 'bot_name', 'powered_by',
            'replace_texts', 'cleanup_user_menu', 'hide_db_manager_link', 'debrand_emails', 'hide_enterprise_upsell',
            'hide_documentation', 'replace_about', 'debrand_bot', 'home_style', 'home_dashboard', 'home_greeting',
            'home_logo_position', 'home_logo_size',
        }
        vals = {key: value for key, value in (values or {}).items() if key in allowed}
        for field_name, data in (images or {}).items():
            if field_name in ('logo', 'app_icon', 'bot_avatar', 'home_background'):
                vals[field_name] = data or False
        if 'home_logo_size' in vals:
            try:
                vals['home_logo_size'] = max(24, min(int(vals['home_logo_size'] or 64), 200))
            except (TypeError, ValueError):
                vals['home_logo_size'] = 64
        if 'brand_name' in vals and not (vals['brand_name'] or '').strip():
            raise UserError(_('The brand name cannot be empty.'))
        config = self._get_config()
        config.write(vals)
        return self.get_dashboard_data()

    @api.model
    def install_companion(self, module_name):
        if not self.env.user.has_group('base.group_system'):
            raise UserError(_('Only administrators can install modules.'))
        if module_name not in [c[0] for c in COMPANIONS]:
            raise UserError(_('Unknown module.'))
        module = self.env['ir.module.module'].sudo().search([('name', '=', module_name)], limit=1)
        if not module:
            raise UserError(_('The module %s is not available on this server.') % module_name)
        if module.state != 'installed':
            module.button_immediate_install()
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    @api.model
    def uninstall_companion(self, module_name):
        if not self.env.user.has_group('base.group_system'):
            raise UserError(_('Only administrators can uninstall modules.'))
        if module_name not in [c[0] for c in COMPANIONS]:
            raise UserError(_('Unknown module.'))
        module = self.env['ir.module.module'].sudo().search([('name', '=', module_name)], limit=1)
        if module.state == 'installed':
            module.button_immediate_uninstall()
        return {'type': 'ir.actions.client', 'tag': 'reload'}
