{
    'name': 'White Label POS',
    'summary': 'Your company look in the Point of Sale: logo, receipts, customer display',
    'version': '18.0.1.0.2',
    'category': 'Productivity',
    'author': 'HIGHTECH PRO',
    'website': 'https://htp.solutions',
    'support': 'contact@htp.solutions',
    'license': 'OPL-1',
    'depends': ['htp_white_label', 'point_of_sale'],
    'data': [
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'htp_white_label_pos/static/src/scss/*.scss',
            'htp_white_label_pos/static/src/xml/*.xml',
            'htp_white_label_pos/static/src/js/*.js',
            'htp_white_label_pos/static/src/v17_19/*',
        ],
        'point_of_sale.customer_display_assets': [
            'htp_white_label_pos/static/src/scss/*.scss',
            'htp_white_label_pos/static/src/xml/*.xml',
            'htp_white_label_pos/static/src/js/*.js',
        ],
    },
    'installable': True,
}
