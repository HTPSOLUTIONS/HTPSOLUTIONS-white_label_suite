from lxml import etree

from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestLivechat(TransactionCase):

    def test_support_page_without_odoo(self):
        arch = self.env.ref('im_livechat.support_page')._get_combined_arch()
        odoo_line = arch.xpath("//div[hasclass('main')]/div[strong]")[0]
        self.assertIn('white.label.config', odoo_line.get('t-if') or '')  # hidden when the branding is on

    def test_french_parent(self):
        """The inheritance must not depend on the English text of the parent template."""
        from odoo.addons.htp_white_label.tests.french import combined_arch_in_french
        archs = combined_arch_in_french(self, ['im_livechat.support_page'], ['im_livechat'])
        arch = etree.fromstring(archs['im_livechat.support_page'])
        self.assertIn('white.label.config', arch.xpath("//div[hasclass('main')]/div[strong]")[0].get('t-if') or '')
