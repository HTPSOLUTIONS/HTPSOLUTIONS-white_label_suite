import hashlib

from odoo import fields, models

from odoo.addons.white_label_kit.models.compat import binary_value, image_bytes


class Website(models.Model):
    _inherit = 'website'

    white_label_kit_favicon = fields.Boolean('Favicon set by White Label', copy=False)

    def _white_label_is_default_favicon(self):
        self.ensure_one()
        if not self.favicon:
            return True
        try:
            default = self._default_favicon()
        except Exception:  # noqa: BLE001 - method missing or file not found: do not touch the favicon
            return False
        return hashlib.sha1(image_bytes(self.favicon)).digest() == hashlib.sha1(image_bytes(default)).digest()

    def _white_label_set_favicon(self, png):
        for website in self:
            if website.white_label_kit_favicon or website._white_label_is_default_favicon():
                website.write({'favicon': binary_value(png), 'white_label_kit_favicon': True})

    def _white_label_restore_favicon(self):
        for website in self.filtered('white_label_kit_favicon'):
            try:
                default = website._default_favicon()
            except Exception:  # noqa: BLE001
                default = False
            website.write({'favicon': default, 'white_label_kit_favicon': False})


class WhiteLabelConfig(models.Model):
    _inherit = 'white.label.config'

    def _white_label_apply_extra(self):
        result = super()._white_label_apply_extra()
        websites = self.env['website'].sudo().search([])
        if not websites:
            return result
        if self.enabled:
            websites._white_label_set_favicon(self._icon_png(256))
        else:
            websites._white_label_restore_favicon()
        return result
