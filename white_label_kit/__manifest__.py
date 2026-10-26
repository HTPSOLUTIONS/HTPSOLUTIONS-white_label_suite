{
    'name': 'White Label Kit',
    'summary': 'Make your Odoo look like your company: name, logo, icon, colors, home screen, e-mails',
    'description': """
White Label
===========
Make your Odoo look like your company, from one dashboard with a live preview.
Nothing changes when the module is installed: choose your settings, then switch on “Apply my branding”.

* browser tab title and favicon, installed-app (PWA) name and icons
* “Powered by” footers (login, portal, website, surveys, e-mails): hidden or “Powered by <your brand>”
* your brand name in the interface texts (messages, error dialogs, settings, help texts)
* a simpler user menu (documentation, odoo.com account, your own help link)
* a tidy Apps menu in Community: only the apps you can install
* the assistant (OdooBot) with the name and picture of your choice
* a home dashboard in your colors: your applications on your background, with your logo
* your logo on the home screen, at the position and size you choose
* optional companion modules for the Website, the Point of Sale, the customer portal, Live Chat
  and the Enterprise home screen: enable only the applications you use.
""",
    'version': '20.0.1.0.2',
    'category': 'Productivity',
    'author': 'HIGHTECH PRO',
    'website': 'https://htp.solutions',
    'support': 'contact@htp.solutions',
    'license': 'OPL-1',
    'depends': ['web', 'mail', 'base_setup'],
    'data': [
        'security/ir.access.csv',
        'views/templates.xml',
        'views/white_label_kit_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'white_label_kit/static/src/scss/white_label_kit.scss',
            'white_label_kit/static/src/xml/white_label_kit.xml',
            'white_label_kit/static/src/js/*.js',
            'white_label_kit/static/src/v20/*',
        ],
        'web.assets_frontend': [
            'white_label_kit/static/src/scss/white_label_kit.scss',
        ],
    },
    'images': ['static/description/banner.png'],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'application': True,
    'installable': True,
}
