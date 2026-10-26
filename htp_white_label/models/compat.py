"""Small helpers so that the same Python code runs on Odoo 17, 18, 19 and 20."""
import base64

try:  # Odoo 20
    from odoo.api import ormcache  # noqa: F401
except ImportError:  # Odoo 17 - 19
    from odoo.tools import ormcache  # noqa: F401

from odoo import release

ODOO_VERSION = release.version_info[0]


def image_bytes(value):
    """Raw bytes of an Image/Binary field value (BinaryValue in 20, base64 bytes before)."""
    if not value:
        return b''
    content = getattr(value, 'content', None)
    if content is not None:
        return bytes(content)
    if isinstance(value, str):
        value = value.encode()
    return base64.b64decode(value)


def binary_value(raw):
    """Value to write in a Binary/Image field from raw bytes (BinaryBytes in 20, base64 before)."""
    try:
        from odoo.tools.binary import BinaryBytes  # Odoo 20
    except ImportError:
        return base64.b64encode(raw)
    return BinaryBytes(raw)


def clear_all_caches(env):
    """Reset the ormcaches (views, templates, translations, our brand data) on every worker."""
    registry = env.registry
    if hasattr(registry, 'clear_all_caches'):  # Odoo 17 - 19
        registry.clear_all_caches()
    elif hasattr(env.transaction, 'invalidate_ormcache'):  # Odoo 20
        for name in ('stable', 'assets', 'templates', 'routing'):
            env.transaction.invalidate_ormcache(name)
    else:
        registry.clear_cache()


def set_config_parameter(env, key, value):
    icp = env['ir.config_parameter'].sudo()
    setter = getattr(icp, 'set_str', None) or icp.set_param
    setter(key, value)
