from odoo import api, models

from ..tools.debrand import debrand_arch, has_brand, remove_enterprise_upsell, replace_brand


def _is_label_pair(item):
    """(value, label) item of a selection field."""
    return isinstance(item, (list, tuple)) and len(item) == 2 and isinstance(item[1], str)


class Base(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def _white_label_data(self):
        if 'white.label.config' not in self.env:
            return {}
        return self.env['white.label.config'].sudo()._brand_data()

    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        data = self._white_label_data()
        if data.get('active'):
            if data.get('replace_texts'):
                debrand_arch(arch, data['name'], data.get('bot_name') if data.get('debrand_bot') else None)
            hide_upsell = data.get('hide_enterprise_upsell') and not data.get('is_enterprise')
            if self._name == 'res.config.settings' and hide_upsell:
                remove_enterprise_upsell(arch)
        return arch, view

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        result = super().fields_get(allfields, attributes)
        data = self._white_label_data()
        if not (data.get('active') and data.get('replace_texts')):
            return result
        brand, bot = data['name'], (data.get('bot_name') if data.get('debrand_bot') else None)
        for description in result.values():
            for key in ('string', 'help'):
                value = description.get(key)
                if isinstance(value, str) and has_brand(value):
                    description[key] = replace_brand(value, brand, bot)
            selection = description.get('selection')
            if isinstance(selection, list) and any(_is_label_pair(item) and 'Odoo' in item[1] for item in selection):
                description['selection'] = [
                    (item[0], replace_brand(item[1], brand, bot)) if _is_label_pair(item) else item
                    for item in selection
                ]
        return result
