import logging

from odoo import api, models
from odoo.tools.misc import file_path

from ..tools.debrand import replace_brand

_logger = logging.getLogger(__name__)

# module name -> tuple of msgids of its .pot file that contain the word Odoo (read once per process)
_POT_MSGIDS = {}


def _unquote(line):
    value = line.strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        value = value[1:-1]
    out, i = [], 0
    while i < len(value):
        char = value[i]
        if char == '\\' and i + 1 < len(value):
            nxt = value[i + 1]
            out.append({'n': '\n', 't': '\t', '"': '"', '\\': '\\'}.get(nxt, '\\' + nxt))
            i += 2
            continue
        out.append(char)
        i += 1
    return ''.join(out)


def odoo_msgids(module):
    """msgids of ``module``'s translation template that mention Odoo (they are not sent to an English browser)."""
    if module in _POT_MSGIDS:
        return _POT_MSGIDS[module]
    found = []
    try:
        path = file_path('%s/i18n/%s.pot' % (module, module))
    except (FileNotFoundError, ValueError, OSError):
        path = None
    if path:
        try:
            with open(path, encoding='utf-8') as pot:
                current, in_msgid = [], False
                for line in pot:
                    if line.startswith('msgid '):
                        current, in_msgid = [_unquote(line[6:])], True
                    elif line.startswith('"') and in_msgid:
                        current.append(_unquote(line))
                    elif line.startswith(('msgstr', 'msgid_plural', 'msgctxt')):
                        if in_msgid:
                            msgid = ''.join(current)
                            if 'Odoo' in msgid:
                                found.append(msgid)
                        in_msgid = False
        except OSError:
            _logger.debug('White Label: cannot read %s', path)
    _POT_MSGIDS[module] = tuple(dict.fromkeys(found))
    return _POT_MSGIDS[module]


class _BrandedTranslations(dict):
    """Marker: translations already rebranded (an override may be reached twice through aliases)."""


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    # ------------------------------------------------------------------ session
    def session_info(self):
        result = super().session_info()
        data = self.env['white.label.config'].sudo()._session_data()
        result['htp_white_label'] = data
        if data.get('active') and data.get('cleanup_user_menu') and 'support_url' in result:
            result['support_url'] = data.get('support_url') or ''
        return result

    @api.model
    def get_frontend_session_info(self):
        result = super().get_frontend_session_info()
        result['htp_white_label'] = self.env['white.label.config'].sudo()._session_data()
        return result

    # ------------------------------------------------------------------ web client translations
    @api.model
    def _white_label_translations(self, translations_per_module):
        if isinstance(translations_per_module, _BrandedTranslations):
            return translations_per_module
        data = self.env['white.label.config'].sudo()._brand_data()
        if not (data.get('active') and data.get('replace_texts')):
            return translations_per_module
        brand, bot = data['name'], (data.get('bot_name') if data.get('debrand_bot') else None)
        result = _BrandedTranslations()
        for module, payload in translations_per_module.items():
            if module.startswith('htp_white_label'):
                # the White Label screens name Odoo on purpose (e.g. "Rename OdooBot")
                result[module] = payload
                continue
            payload = dict(payload or {})
            messages = payload.get('messages') or ()
            if isinstance(messages, dict):  # defensive: {msgid: translation}
                messages = [{'id': key, 'string': value} for key, value in messages.items()]
            known = set()
            new_messages = []
            for message in messages:
                known.add(message.get('id'))
                text = message.get('string') or ''
                if 'Odoo' in text:
                    message = dict(message, string=replace_brand(text, brand, bot))
                new_messages.append(message)
            for msgid in odoo_msgids(module):
                if msgid not in known:
                    new_messages.append({'id': msgid, 'string': replace_brand(msgid, brand, bot)})
            payload['messages'] = new_messages
            result[module] = payload
        return result

    @api.model
    def get_translations_for_webclient(self, modules, lang):  # Odoo 17 - 18
        translations, lang_params = super().get_translations_for_webclient(modules, lang)
        return self._white_label_translations(translations), lang_params

    @api.model
    def _get_translations_for_webclient(self, modules, lang):  # Odoo 19 - 20
        translations, lang_params = super()._get_translations_for_webclient(modules, lang)
        return self._white_label_translations(translations), lang_params
