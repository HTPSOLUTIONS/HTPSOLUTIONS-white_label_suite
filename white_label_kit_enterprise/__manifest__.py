{
    'name': 'Brand Kit – Home Screen',
    'summary': "Your background and logo (position and size of your choice) on the Enterprise home screen. White "
               "label Odoo Enterprise, rebranding of the home page. Marque blanche : fond et logo de l'écran "
               "d'accueil Odoo Enterprise.",
    'version': '19.0.1.0.3',
    'category': 'Productivity',
    'author': 'HIGHTECH PRO',
    'website': 'https://htp.solutions',
    'support': 'contact@htp.solutions',
    'license': 'OPL-1',
    'depends': ['white_label_kit', 'web_enterprise'],
    'assets': {
        'web.assets_backend': ['white_label_kit_enterprise/static/src/scss/*.scss'],
        'web.assets_frontend': ['white_label_kit_enterprise/static/src/scss/*.scss'],
    },
    'images': ['static/description/banner.gif'],
    'installable': True,
}
