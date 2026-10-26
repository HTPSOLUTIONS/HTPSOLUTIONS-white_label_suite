from lxml import etree

from odoo.tests import BaseCase, tagged

from ..tools.debrand import debrand_arch, debrand_email_html, remove_enterprise_upsell, replace_brand


@tagged('post_install', '-at_install')
class TestDebrandHelpers(BaseCase):

    def test_replace_brand_keeps_urls_and_identifiers(self):
        text = 'Odoo needs you. See www.odoo.com or https://odoo.sh/x. odoo_logo, OdooBot and Odoo S.A.'
        self.assertEqual(replace_brand(text, 'Acme', 'Max'),
                         'Acme needs you. See www.odoo.com or https://odoo.sh/x. odoo_logo, Max and Acme')
        self.assertEqual(replace_brand('Odoo Server Error', 'Acme'), 'Acme Server Error')
        self.assertEqual(replace_brand('Nothing here', 'Acme'), 'Nothing here')

    def test_email_footer(self):
        html = ('<div>Hello</div><div>Powered by <a target="_blank" href="https://www.odoo.com?utm_source=db&amp;'
                'utm_medium=email" style="color: #875A7B;">Odoo</a></div><p>Sent using Odoo</p>')
        hidden = debrand_email_html(html, 'Acme', 'https://acme.example', 'hide')
        self.assertNotIn('odoo', hidden.lower())
        self.assertIn('<div>Hello</div><div></div>', hidden, 'the HTML structure is kept')
        branded = debrand_email_html(html, 'Acme', None, 'brand')
        self.assertIn('Powered by Acme', branded)
        self.assertNotIn('odoo.com', branded)

    def test_arch(self):
        arch = etree.fromstring(
            '<form><field name="x" help="Odoo will do it" placeholder="Odoo"/><span>Welcome to Odoo</span>'
            '<setting><field name="module_x" widget="upgrade_boolean"/></setting></form>')
        debrand_arch(arch, 'Acme')
        self.assertEqual(arch[0].get('help'), 'Acme will do it')
        self.assertEqual(arch[0].get('placeholder'), 'Acme')
        self.assertEqual(arch[1].text, 'Welcome to Acme')
        self.assertEqual(remove_enterprise_upsell(arch), 1)
        self.assertFalse(arch.xpath('//setting'))
