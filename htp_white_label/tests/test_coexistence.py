from lxml import etree

from odoo.tests import TransactionCase, tagged

# like the “remove Powered by Odoo” modules of the Odoo Apps store
OTHER_LOGIN = (
    """<data><xpath expr="//div[hasclass('card-body')]//div[hasclass('text-center') and hasclass('small')]"""
    """/a[contains(@href, 'odoo.com')]" position="replace"/></data>"""
)


@tagged('post_install', '-at_install')
class TestCoexistence(TransactionCase):
    """Other debranding modules change the same elements: whatever the order, neither side may break the page."""

    def setUp(self):
        super().setUp()
        # with the Website app, the login page uses the website layout instead of the card of web.login_layout
        website_login = self.env.ref('website.login_layout', raise_if_not_found=False)
        if website_login:
            website_login.active = False

    def _other_view(self, xmlid, arch, priority):
        return self.env['ir.ui.view'].create({
            'name': 'other debranding', 'type': 'qweb', 'inherit_id': self.env.ref(xmlid).id,
            'priority': priority, 'key': 'other_debranding.view_%s' % priority, 'arch': arch,
        })

    def test_odoo_link_hidden_not_removed(self):
        arch = self.env.ref('web.login_layout')._get_combined_arch()
        link = arch.xpath("//a[contains(@href, 'utm_medium=auth')]")
        self.assertTrue(link)
        self.assertIn('white.label.config', link[0].get('t-if') or '')

    def test_login_page_with_other_module(self):
        for priority in (1, 99):  # applied before, then after White Label
            other = self._other_view('web.login_layout', OTHER_LOGIN, priority)
            arch = etree.tostring(self.env.ref('web.login_layout')._get_combined_arch(), encoding='unicode')
            self.assertNotIn('utm_medium=auth', arch)
            self.assertIn('hide_db_manager_link', arch)  # the other White Label change of the page still applies
            other.unlink()

    def test_other_views_still_strict(self):
        """Only White Label views skip a missing target: any other broken view still raises."""
        broken = '<data><xpath expr="//div[@id=\'wl_does_not_exist\']" position="replace"/></data>'
        with self.assertRaises(Exception):
            other = self._other_view('web.login_layout', broken, 50)
            self.env.ref('web.login_layout')._get_combined_arch()
            other.unlink()
