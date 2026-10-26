import base64

from odoo.tests import HttpCase, TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestSwitch(TransactionCase):
    """Installing the module changes nothing: the branding applies only once “Apply my branding” is on."""

    def setUp(self):
        super().setUp()
        self.Config = self.env['white.label.config']
        self.config = self.Config._get_config()

    def test_off_after_install(self):
        self.assertFalse(self.config.enabled)
        self.assertEqual(self.config.home_style, 'default')
        self.assertFalse(self.config.color_navbar)
        data = self.Config._brand_data()
        self.assertFalse(data['active'])
        self.assertNotIn('name', data)
        self.assertNotIn('css_vars', data)

    def test_switch_on_then_off_restores_everything(self):
        bot = self.env.ref('base.partner_root')
        bot_name = bot.name
        params = self.env['ir.config_parameter'].sudo()
        app_name = params.search([('key', '=', 'web.web_app_name')]).value
        self.config.write({'enabled': True, 'brand_name': 'Acme Cloud', 'bot_name': 'Max', 'debrand_bot': True})
        self.assertTrue(self.Config._brand_data()['active'])
        self.assertEqual(bot.name, 'Max')
        if 'web_app_name' in self.env['res.config.settings']._fields:
            self.assertEqual(params.search([('key', '=', 'web.web_app_name')]).value, 'Acme Cloud')
        self.config.enabled = False
        self.assertFalse(self.Config._brand_data()['active'])
        self.assertEqual(bot.name, bot_name)
        self.assertEqual(params.search([('key', '=', 'web.web_app_name')]).value, app_name)

    def test_home_logo_options(self):
        logo = base64.b64encode(self.config._icon_png(64)).decode()
        self.config.write({'enabled': True, 'logo': logo, 'home_logo_position': 'left', 'home_logo_size': 90})
        data = self.Config._brand_data()
        self.assertIn('o_wl_has_home_logo', data['body_class'])
        self.assertIn('o_wl_home_logo_left', data['body_class'])
        self.assertIn('--wl-home-logo-size: 90px', data['css_vars'])
        self.config.home_logo_position = 'none'
        self.assertNotIn('o_wl_has_home_logo', self.Config._brand_data()['body_class'])
        result = self.Config.save_dashboard({'home_logo_position': 'right', 'home_logo_size': '500'})
        self.assertEqual(result['values']['home_logo_size'], 200)
        self.assertIn('o_wl_home_logo_right', self.Config._brand_data()['body_class'])


@tagged('post_install', '-at_install')
class TestDefaultLook(HttpCase):

    def test_login_page_unchanged(self):
        html = self.url_open('/web/login').text
        self.assertNotIn('o_wl_active', html)
        self.assertNotIn('--wl-color', html)
        self.assertNotIn('/white_label_kit/icon', html)
