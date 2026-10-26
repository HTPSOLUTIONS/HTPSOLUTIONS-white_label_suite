import json

from odoo import http
from odoo.http import request

from odoo.addons.web.controllers.webmanifest import WebManifest

ONE_DAY = 24 * 3600
ONE_YEAR = 365 * ONE_DAY


def _config():
    return request.env['white.label.config'].sudo()._get_config()


def _cache_headers(versioned):
    value = 'public, max-age=%d, immutable' % ONE_YEAR if versioned else 'public, max-age=%d' % ONE_DAY
    return [('Cache-Control', value)]


class WhiteLabelController(http.Controller):

    @http.route(['/htp_white_label/icon/<int:size>', '/htp_white_label/favicon.ico'], type='http', auth='public',
                methods=['GET'], sitemap=False)
    def icon(self, size=64, v=None, **kwargs):
        png = _config()._icon_png(size)
        headers = [('Content-Type', 'image/png'), ('Content-Length', str(len(png)))] + _cache_headers(bool(v))
        return request.make_response(png, headers)

    def _image_response(self, field_name, v=None, width=0, height=0):
        config = _config()
        if not config[field_name]:
            return None
        stream = request.env['ir.binary']._get_image_stream_from(
            config, field_name, width=int(width or 0), height=int(height or 0))
        return stream.get_response(max_age=ONE_YEAR if v else ONE_DAY)

    @http.route('/htp_white_label/logo', type='http', auth='public', methods=['GET'], sitemap=False)
    def logo(self, v=None, **kwargs):
        response = self._image_response('logo', v)
        if response is None:
            return request.redirect('/web/binary/company_logo', 302, local=True)
        return response

    @http.route('/htp_white_label/home_background', type='http', auth='public', methods=['GET'], sitemap=False)
    def home_background(self, v=None, **kwargs):
        response = self._image_response('home_background', v)
        if response is None:
            return request.not_found()
        return response


class WhiteLabelWebManifest(WebManifest):
    """Installed app (PWA): name, icons and colors of the brand instead of Odoo."""

    def _white_label_manifest(self, manifest):
        data = request.env['white.label.config'].sudo()._brand_data()
        if not data.get('active'):
            return manifest
        stamp = data.get('stamp', '0')
        manifest['name'] = data['name']
        manifest['short_name'] = data['name'][:12]
        manifest['theme_color'] = data.get('color') or manifest.get('theme_color')
        manifest['icons'] = [{
            'src': '/htp_white_label/icon/%d?v=%s' % (size, stamp),
            'sizes': '%dx%d' % (size, size),
            'type': 'image/png',
        } for size in (192, 512)]
        return manifest

    @http.route()
    def webmanifest(self, *args, **kwargs):
        response = super().webmanifest(*args, **kwargs)
        try:
            manifest = json.loads(response.get_data())
        except (ValueError, AttributeError):
            return response
        manifest = self._white_label_manifest(manifest)
        body = json.dumps(manifest)
        response.set_data(body)
        response.headers['Content-Length'] = str(len(response.get_data()))
        return response
