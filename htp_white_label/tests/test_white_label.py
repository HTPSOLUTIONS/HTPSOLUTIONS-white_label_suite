import re

from markupsafe import Markup

from odoo import release
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, new_test_user, tagged

ODOO_WORD = re.compile(r'(?<![\w./@:-])Odoo(?![\w-]|\.(?:com|sh)\b)')


@tagged('post_install', '-at_install')
class TestWhiteLabel(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.config = cls.env['white.label.config']._get_config()
        cls.config.write({
            'enabled': True, 'brand_name': 'Acme Cloud', 'brand_website': 'https://acme.example',
            'support_url': 'https://help.acme.example',
            'bot_name': 'Max', 'powered_by': 'hide', 'replace_texts': True, 'debrand_emails': True,
            'hide_enterprise_upsell': True, 'debrand_bot': True, 'cleanup_user_menu': True,
        })
        cls.Config = cls.env['white.label.config']

    def test_single_config(self):
        self.assertEqual(self.Config.search_count([]), 1)
        with self.assertRaises(UserError):
            self.Config.create({})
        with self.assertRaises(UserError):
            self.config.unlink()

    def test_brand_data(self):
        data = self.Config._brand_data()
        self.assertTrue(data['active'])
        self.assertEqual(data['name'], 'Acme Cloud')
        self.assertIn('--wl-color', data['css_vars'])
        session = self.Config._session_data()
        self.assertEqual(session['name'], 'Acme Cloud')
        self.assertTrue(session['favicon_url'].startswith('/htp_white_label/icon/64'))
        self.assertEqual(session['support_url'], 'https://help.acme.example')

    def test_color_check(self):
        with self.assertRaises(UserError):
            self.config.color = 'red'
        self.config.color = '#AA0000'
        self.assertEqual(self.config.color, '#aa0000')

    def test_bot_renamed_and_restored(self):
        bot = self.env.ref('base.partner_root')
        self.assertEqual(bot.name, 'Max')
        self.config.debrand_bot = False
        self.assertEqual(bot.name, self.config.original_bot_name)
        self.assertNotEqual(bot.name, 'Max')

    def test_apps_menu(self):
        action = self.env.ref('base.open_module_tree')
        if self.Config._brand_data()['is_enterprise']:
            self.assertNotEqual(action.domain, "[('to_buy', '=', False)]")
        else:
            self.assertEqual(action.domain, "[('to_buy', '=', False)]")
            self.config.hide_enterprise_upsell = False
            self.assertNotEqual(action.domain, "[('to_buy', '=', False)]")

    def test_web_client_translations(self):
        IrHttp = self.env['ir.http']
        if release.version_info[0] >= 19:
            translations, _params = IrHttp._get_translations_for_webclient(['web'], 'en_US')
        else:
            translations, _params = IrHttp.get_translations_for_webclient(['web'], 'en_US')
        strings = {m['id']: m['string'] for m in translations['web']['messages']}
        self.assertEqual(strings.get('Odoo Server Error'), 'Acme Cloud Server Error')
        self.assertFalse([s for s in strings.values() if ODOO_WORD.search(s)])

    def test_views_and_fields(self):
        arch = self.env['res.config.settings'].get_views([(False, 'form')])['views']['form']['arch']
        self.assertIn('Acme Cloud', arch)
        if not self.Config._brand_data()['is_enterprise']:
            self.assertNotIn('upgrade_boolean', arch)
        fields = self.env['res.config.settings'].fields_get(attributes=['string', 'help'])
        leftovers = [name for name, desc in fields.items()
                     if any(ODOO_WORD.search(desc.get(key) or '') for key in ('string', 'help'))]
        self.assertFalse(leftovers)

    def test_mail_cleaned(self):
        mail = self.env['mail.mail'].create({
            'subject': 'Welcome to Odoo',
            'email_to': 'someone@example.com',
            'body_html': Markup('<p>Hi</p><p>Powered by <a href="https://www.odoo.com?utm_source=db">Odoo</a></p>'),
        })
        self.assertEqual(mail.subject, 'Welcome to Acme Cloud')
        self.assertNotIn('odoo', str(mail.body_html).lower())
        self.config.debrand_emails = False
        mail2 = self.env['mail.mail'].create({'body_html': '<p>Powered by <a href="https://www.odoo.com">Odoo</a></p>'})
        self.assertIn('odoo.com', str(mail2.body_html))

    def test_icon(self):
        png = self.config._icon_png(64)
        self.assertTrue(png.startswith(b'\x89PNG'))
        self.assertGreater(len(png), 100)

    def test_dashboard_api(self):
        data = self.Config.get_dashboard_data()
        self.assertEqual(data['values']['brand_name'], 'Acme Cloud')
        self.assertIsInstance(data['companions'], list)
        result = self.Config.save_dashboard({'brand_name': 'Acme 2', 'name': 'Not allowed'}, {'logo': False})
        self.assertEqual(result['values']['brand_name'], 'Acme 2')
        self.assertEqual(self.config.name, 'White Label')
        user = new_test_user(self.env, 'wl_simple_user', groups='base.group_user')
        with self.assertRaises(UserError):
            self.Config.with_user(user).get_dashboard_data()
        with self.assertRaises(UserError):
            self.Config.with_user(user).save_dashboard({'brand_name': 'x'})
