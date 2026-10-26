"""Text helpers: replace the Odoo brand by the configured brand.

Pure functions (no ORM) so that they can be unit-tested and reused by the web client payloads,
view architectures, field descriptions and outgoing emails.
"""
import re

# "Odoo" as a word, but not inside a URL or a domain name (odoo.com, odoo.sh, www.odoo…),
# an identifier (odoo_logo, OdooBot, odoo-bin) or an e-mail address.
_WORD_RE = re.compile(r'(?<![\w./@:-])Odoo(?![\w-]|\.(?:com|sh|net)\b)')
_BOT_RE = re.compile(r'(?<![\w./@-])OdooBot(?![\w-])')
_ODOO_SA_RE = re.compile(r'Odoo\s+S\.?A\.?')

# Outgoing e-mails: footers and links added by the standard layouts
_EMAIL_POWERED_RE = re.compile(r'Powered\s+by\s*<a\b[^>]*odoo\.com[^>]*>.*?</a>', re.IGNORECASE | re.DOTALL)
_EMAIL_LINK_RE = re.compile(r'''href=(["'])https?://(?:www\.)?odoo\.com[^"']*\1''', re.IGNORECASE)
_EMAIL_ANCHOR_TEXT_RE = re.compile(r'(<a\b[^>]*>)\s*Odoo\s*(</a>)')
_EMAIL_USING_RE = re.compile(r'\b(using|with|via)\s+Odoo\b', re.IGNORECASE)
_EMAIL_ODOO_ANCHOR_RE = re.compile(
    r'''<a\b[^>]*href=["']https?://(?:www\.)?odoo\.com[^"']*["'][^>]*>(.*?)</a>''', re.IGNORECASE | re.DOTALL)


def has_brand(text):
    return bool(text) and 'Odoo' in text


def replace_brand(text, brand_name, bot_name=None):
    """Replace the Odoo brand in a user-visible text. URLs and identifiers are left untouched."""
    if not text or 'Odoo' not in text or not brand_name:
        return text
    if bot_name:
        text = _BOT_RE.sub(bot_name, text)
    text = _ODOO_SA_RE.sub(brand_name, text)
    return _WORD_RE.sub(brand_name, text)


def debrand_email_html(html, brand_name, brand_url=None, mode='hide'):
    """Remove (or rebrand) the “Powered by Odoo” footers and the links to odoo.com of an e-mail body."""
    if not html or ('odoo' not in html.lower()):
        return html
    if mode == 'brand' and brand_name:
        if brand_url:
            replacement = 'Powered by <a target="_blank" href="%s" style="color: inherit;">%s</a>' % (
                _escape(brand_url), _escape(brand_name))
        else:
            replacement = 'Powered by %s' % _escape(brand_name)
    else:
        replacement = ''
    html = _EMAIL_POWERED_RE.sub(replacement, html)
    if brand_name:
        html = _EMAIL_ANCHOR_TEXT_RE.sub(lambda m: '%s%s%s' % (m.group(1), _escape(brand_name), m.group(2)), html)
        html = _EMAIL_USING_RE.sub(lambda m: '%s %s' % (m.group(1), _escape(brand_name)), html)
    if brand_url:
        html = _EMAIL_LINK_RE.sub(lambda m: 'href=%s%s%s' % (m.group(1), _escape(brand_url), m.group(1)), html)
    else:
        # no brand website: keep the text, drop the link to odoo.com
        html = _EMAIL_ODOO_ANCHOR_RE.sub(lambda m: m.group(1), html)
    return html


def debrand_subject(subject, brand_name):
    return replace_brand(subject, brand_name) if subject else subject


def _escape(value):
    return (str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            .replace('"', '&quot;'))


# attributes of view architectures that hold user-visible texts
ARCH_TEXT_ATTRIBUTES = ('string', 'help', 'placeholder', 'title', 'confirm', 'aria-label', 'data-tooltip', 'sum')


def debrand_arch(arch, brand_name, bot_name=None):
    """Replace the brand in the texts and labels of a view architecture (lxml element, modified in place)."""
    if arch is None or not brand_name:
        return False
    changed = False
    for node in arch.iter():
        if not isinstance(node.tag, str):
            continue
        for attr in ARCH_TEXT_ATTRIBUTES:
            value = node.get(attr)
            if value and 'Odoo' in value:
                new = replace_brand(value, brand_name, bot_name)
                if new != value:
                    node.set(attr, new)
                    changed = True
        if node.text and 'Odoo' in node.text:
            new = replace_brand(node.text, brand_name, bot_name)
            if new != node.text:
                node.text = new
                changed = True
        if node.tail and 'Odoo' in node.tail:
            new = replace_brand(node.tail, brand_name, bot_name)
            if new != node.tail:
                node.tail = new
                changed = True
    return changed


def remove_enterprise_upsell(arch):
    """Settings form: remove the settings that only exist to advertise Odoo Enterprise (upgrade_boolean)."""
    removed = 0
    for field in arch.xpath("//field[@widget='upgrade_boolean']"):
        container = field
        while (container is not None and container.tag != 'setting'
               and 'o_setting_box' not in (container.get('class') or '')):
            container = container.getparent()
        target = container if container is not None else field
        parent = target.getparent()
        if parent is not None:
            parent.remove(target)
            removed += 1
    return removed
