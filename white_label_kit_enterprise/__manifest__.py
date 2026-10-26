{
    'name': 'White Label Enterprise',
    'summary': 'Your background and logo (position and size of your choice) on the Enterprise home screen',
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
    'images': ['static/description/banner.png'],
    'installable': True,
}
