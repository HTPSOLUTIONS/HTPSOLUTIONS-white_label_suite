from markupsafe import Markup

from odoo import api, models

from ..tools.debrand import debrand_email_html, debrand_subject


class MailMail(models.Model):
    _inherit = 'mail.mail'

    @api.model
    def _white_label_clean(self, vals):
        data = self.env['white.label.config'].sudo()._brand_data()
        if not (data.get('active') and data.get('debrand_emails')):
            return vals
        body = vals.get('body_html')
        if body and 'odoo' in str(body).lower():
            cleaned = debrand_email_html(str(body), data['name'], data.get('website') or None, data.get('powered_by'))
            vals['body_html'] = Markup(cleaned) if isinstance(body, Markup) else cleaned
        if vals.get('subject') and data.get('replace_texts'):
            vals['subject'] = debrand_subject(vals['subject'], data['name'])
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        return super().create([self._white_label_clean(dict(vals)) for vals in vals_list])

    def write(self, vals):
        if 'body_html' in vals or 'subject' in vals:
            vals = self._white_label_clean(dict(vals))
        return super().write(vals)
