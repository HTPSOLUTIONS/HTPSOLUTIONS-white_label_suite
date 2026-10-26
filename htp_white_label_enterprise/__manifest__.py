{
    'name': 'White Label Enterprise',
    'summary': 'Your background and logo (position and size of your choice) on the Enterprise home screen',
    'version': '19.0.1.0.2',
    'category': 'Productivity',
    'author': 'HIGHTECH PRO',
    'website': 'https://htp.solutions',
    'support': 'contact@htp.solutions',
    'license': 'OPL-1',
    'depends': ['htp_white_label', 'web_enterprise'],
    'assets': {
        'web.assets_backend': ['htp_white_label_enterprise/static/src/scss/*.scss'],
        'web.assets_frontend': ['htp_white_label_enterprise/static/src/scss/*.scss'],
    },
    'installable': True,
}
