{
    'name': 'White Label POS',
    'summary': 'Your company look in the Point of Sale: logo, receipts, customer display',
    'version': '18.0.1.0.3',
    'category': 'Productivity',
    'author': 'HIGHTECH PRO',
    'website': 'https://htp.solutions',
    'support': 'contact@htp.solutions',
    'license': 'OPL-1',
    'depends': ['white_label_kit', 'point_of_sale'],
    'data': [
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'white_label_kit_pos/static/src/scss/*.scss',
            'white_label_kit_pos/static/src/xml/*.xml',
            'white_label_kit_pos/static/src/js/*.js',
            'white_label_kit_pos/static/src/v17_19/*',
        ],
        'point_of_sale.customer_display_assets': [
            'white_label_kit_pos/static/src/scss/*.scss',
            'white_label_kit_pos/static/src/xml/*.xml',
            'white_label_kit_pos/static/src/js/*.js',
        ],
    },
    'images': ['static/description/banner.png'],
    'installable': True,
}
