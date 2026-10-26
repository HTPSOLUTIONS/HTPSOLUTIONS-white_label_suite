import base64

from odoo.tests import HttpCase, tagged


@tagged('post_install', '-at_install')
class TestEnterprise(HttpCase):

    def test_login_page_style(self):
        config = self.env['white.label.config']._get_config()
        html = self.url_open('/web/login').text
        self.assertNotIn('o_wl_home_style', html)  # off after install: standard Enterprise look
        logo = base64.b64encode(config._icon_png(64)).decode()
        config.write({'enabled': True, 'brand_name': 'Acme Cloud', 'home_style': 'gradient', 'logo': logo,
                      'home_logo_position': 'right', 'home_logo_size': 80})
        html = self.url_open('/web/login').text
        self.assertIn('o_wl_home_style_gradient', html)
        self.assertIn('o_wl_home_logo_right', html)
        self.assertIn('--wl-home-logo-size: 80px', html)
