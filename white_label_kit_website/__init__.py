from . import models


def post_init_hook(env):
    config = env['white.label.config'].sudo().search([], limit=1)
    if config:
        config._apply()


def uninstall_hook(env):
    env['website'].sudo().search([('white_label_kit_favicon', '=', True)])._white_label_restore_favicon()
