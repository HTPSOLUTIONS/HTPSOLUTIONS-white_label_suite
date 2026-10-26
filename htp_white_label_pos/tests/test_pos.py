from lxml import etree

from odoo import release
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestPos(TransactionCase):

    def test_receipt_footer(self):
        if release.version_info[0] < 20:
            self.skipTest('Odoo 17 - 19: the receipt is an Owl template, checked in the browser')
        arch = self.env.ref('point_of_sale.pos_order_receipt_footer')._get_combined_arch()
        odoo_line = arch.xpath("//div[@name='footer']/../div[strong]")[0]
        self.assertIn('white.label.config', odoo_line.get('t-if') or '')  # hidden when the branding is on

    def test_french_parent(self):
        """The inheritance must not depend on the English text of the parent template."""
        if release.version_info[0] < 20:
            self.skipTest('Odoo 17 - 19: Owl receipt')
        from odoo.addons.htp_white_label.tests.french import combined_arch_in_french
        archs = combined_arch_in_french(self, ['point_of_sale.pos_order_receipt_footer'], ['point_of_sale'])
        arch = etree.fromstring(archs['point_of_sale.pos_order_receipt_footer'])
        self.assertIn('white.label.config', arch.xpath("//div[@name='footer']/../div[strong]")[0].get('t-if') or '')

    # Odoo 17 - 19: Owl receipt. The changes are applied by the server (17) or the browser (18, 19) with the same
    # xpath rules as lxml: a missing target breaks the receipt (the whole POS on 17).
    def _owl_receipt(self):
        from odoo.tools import file_open
        parser = etree.XMLParser(remove_comments=True)
        path = 'point_of_sale/static/src/app/screens/receipt_screen/receipt/order_receipt.xml'
        with file_open(path, 'rb') as f:
            root = etree.parse(f, parser).getroot()
        return root.xpath("//t[@t-name='point_of_sale.OrderReceipt']")[0]

    def _white_label_receipt_changes(self):
        from odoo.tools import file_open
        parser = etree.XMLParser(remove_comments=True)
        with file_open('htp_white_label_pos/static/src/v17_19/order_receipt.xml', 'rb') as f:
            root = etree.parse(f, parser).getroot()
        return list(root.xpath("//t[@t-inherit='point_of_sale.OrderReceipt']")[0])

    def test_owl_receipt_with_other_module(self):
        if release.version_info[0] >= 20:
            self.skipTest('Odoo 20: server receipt')
        from odoo.tools.template_inheritance import apply_inheritance_specs
        other = """<t><xpath expr="//*[starts-with(normalize-space(text()), 'Powered by')]" position="replace"/></t>"""
        for order in ('alone', 'htp_white_label_first', 'other_first'):
            receipt = self._owl_receipt()
            ours = self._white_label_receipt_changes()
            theirs = list(etree.fromstring(other))
            if order == 'other_first':
                receipt = apply_inheritance_specs(receipt, theirs)
            receipt = apply_inheritance_specs(receipt, ours)
            if order == 'htp_white_label_first':
                receipt = apply_inheritance_specs(receipt, theirs)
            self.assertEqual(len(receipt.xpath("//p[@t-out='this.wlPoweredBy']")), 1, order)
            for node in receipt.xpath("//*[starts-with(normalize-space(text()), 'Powered by')]"):
                self.assertEqual(node.get('t-if'), 'false', order)
            # still one root element (the receipt is rendered as a single block)
            self.assertEqual(len(receipt), 1, order)
