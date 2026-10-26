import json
import re  # noqa: F401

from odoo.tests import HttpCase, tagged


@tagged('post_install', '-at_install')
class TestWhiteLabelHttp(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env['white.label.config']._get_config().write({
            'enabled': True, 'brand_name': 'Acme Cloud', 'powered_by': 'brand', 'brand_website': 'https://acme.example',
            'hide_db_manager_link': True, 'replace_texts': True,
        })

    def test_login_page(self):
        response = self.url_open('/web/login')
        self.assertEqual(response.status_code, 200)
        html = response.text
        self.assertIn('Acme Cloud', html)
        self.assertNotIn('utm_medium=auth', html)
        self.assertNotRegex(html, r'Powered by\s*(<[^>]+>\s*)*Odoo')
        self.assertNotIn('/web/database/manager', html)
        self.assertIn('--wl-color', html)
        if 'website' not in self.env.registry._init_modules:
            self.assertIn('<title>Acme Cloud</title>', html)
            self.assertIn('/white_label_kit/icon/64', html)
            self.assertIn('Powered by <span>Acme Cloud</span>', html)

    def test_icon_and_manifest(self):
        response = self.url_open('/white_label_kit/icon/64?v=1')
        self.assertEqual(response.headers['Content-Type'], 'image/png')
        self.assertTrue(response.content.startswith(b'\x89PNG'))
        self.authenticate('admin', 'admin')
        manifest = json.loads(self.url_open('/web/manifest.webmanifest').content)
        self.assertEqual(manifest['name'], 'Acme Cloud')
        self.assertTrue(all(icon['src'].startswith('/white_label_kit/icon/') for icon in manifest['icons']))

    def test_backend_session(self):
        self.authenticate('admin', 'admin')
        html = self.url_open('/odoo' if self.url_open('/odoo').status_code == 200 else '/web').text
        self.assertIn('"white_label_kit"', html)
        self.assertIn('Acme Cloud', html)
        self.assertIn('/white_label_kit/icon/180', html)

    def test_logo_fallback(self):
        response = self.url_open('/white_label_kit/logo', allow_redirects=False)
        self.assertIn(response.status_code, (301, 302, 303))
