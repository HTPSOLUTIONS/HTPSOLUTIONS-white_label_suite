def post_init_hook(env):
    """Create the settings with the main company as brand. Nothing changes until “Apply my branding” is switched on."""
    config = env['white.label.config'].sudo()._get_config()
    company = env.ref('base.main_company', raise_if_not_found=False) or env.company
    if company and company.name and config.brand_name in (False, '', 'My Company', 'YourCompany'):
        config.write({'brand_name': company.name})


def uninstall_hook(env):
    """Put back what the module changed outside its own records."""
    config = env['white.label.config'].sudo().search([], limit=1)
    if config:
        config._restore_bot()
        config._restore_apps_menu()
        config._restore_web_app_name()
    if 'web_app_name' in env['res.config.settings']._fields:
        params = env['ir.config_parameter'].sudo().search([('key', '=', 'web.web_app_name')])
        if config and params.filtered(lambda p: p.value == config.brand_name):
            params.unlink()
