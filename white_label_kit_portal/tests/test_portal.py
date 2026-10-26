from lxml import etree

from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestPortal(TransactionCase):

    def setUp(self):
        super().setUp()
        self.config = self.env['white.label.config']._get_config()

    def test_sidebar_standard_when_off(self):
        self.assertIn('utm_medium=portal', self._render_sidebar())

    def _render_sidebar(self):
        return str(self.env['ir.qweb']._render('portal.portal_record_sidebar', {'classes': ''}))

    def test_sidebar_without_odoo(self):
        self.config.enabled = True
        html = self._render_sidebar()
        self.assertNotIn('utm_medium=portal', html)
        self.assertNotIn('/web/static/img/logo.png', html)

    def test_sidebar_brand(self):
        self.config.write({'enabled': True, 'brand_name': 'Acme Cloud', 'powered_by': 'brand'})
        html = self._render_sidebar()
        self.assertIn('Acme Cloud', html)
        self.assertNotIn('utm_medium=portal', html)

    def test_french_parent(self):
        """The inheritance must not depend on the English text of the parent template."""
        from odoo.addons.white_label_kit.tests.french import combined_arch_in_french
        archs = combined_arch_in_french(self, ['portal.portal_record_sidebar'], ['portal'])
        arch = etree.fromstring(archs['portal.portal_record_sidebar'])
        link = arch.xpath("//a[contains(@href, 'utm_medium=portal')]/..")
        self.assertTrue(link and 'white.label.config' in (link[0].get('t-if') or ''))

    def test_other_debranding_module(self):
        """Another module removing the same line, before or after White Label, must not break the page."""
        self.config.enabled = True
        parent = self.env.ref('portal.portal_record_sidebar')
        for priority in (1, 99):
            other = self.env['ir.ui.view'].create({
                'name': 'other debranding', 'type': 'qweb', 'inherit_id': parent.id, 'priority': priority,
                'key': 'other_debranding.sidebar_%s' % priority,
                'arch': ("""<data><xpath expr="//div[hasclass('text-muted') and contains(., 'Powered by')]" """
                         """position="replace"/></data>"""),
            })
            html = self._render_sidebar()
            self.assertNotIn('utm_medium=portal', html)
            other.unlink()
