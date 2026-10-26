from lxml import etree

from odoo.tests import HttpCase, tagged


@tagged('post_install', '-at_install')
class TestWebsite(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.config = cls.env['white.label.config']._get_config()
        cls.config.write({'enabled': True, 'brand_name': 'Acme Cloud', 'powered_by': 'hide'})

    def test_favicon_and_generator(self):
        website = self.env['website'].search([], limit=1)
        self.assertTrue(website.htp_white_label_favicon)
        html = self.url_open('/').text
        self.assertIn('content="Acme Cloud"', html)
        self.assertNotIn('content="Odoo"', html)
        self.assertNotRegex(html, r'Powered by\s*(<[^>]+>\s*)*Odoo')

    def test_favicon_restored_when_off(self):
        website = self.env['website'].search([], limit=1)
        self.config.enabled = False
        self.assertFalse(website.htp_white_label_favicon)
        self.assertIn('content="Odoo"', self.url_open('/').text)

    def test_restore_favicon(self):
        website = self.env['website'].search([], limit=1)
        website._white_label_restore_favicon()
        self.assertFalse(website.htp_white_label_favicon)

    def test_french_info_page(self):
        from odoo.addons.htp_white_label.tests.french import combined_arch_in_french
        self.env.ref('website.show_website_info').active = True
        archs = combined_arch_in_french(self, ['website.website_info'], ['website'])
        arch = etree.fromstring(archs['website.website_info'])
        versions = arch.xpath("//h1/small[@groups='base.group_no_one']")
        self.assertEqual(len(versions), 2)  # Odoo's line, hidden when the branding is on, and White Label's
        self.assertIn('white.label.config', versions[0].get('t-if') or '')
        lines = arch.xpath("//h1/following-sibling::p")
        self.assertIn('white.label.config', lines[0].get('t-if') or '')
