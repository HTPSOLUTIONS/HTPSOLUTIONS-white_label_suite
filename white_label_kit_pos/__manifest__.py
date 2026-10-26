{
    'name': 'White Label POS',
    'summary': 'Your company look in the Point of Sale: logo, receipts, customer display',
    'version': '20.0.1.0.2',
    'category': 'Productivity',
    'author': 'HIGHTECH PRO',
    'website': 'https://htp.solutions',
    'support': 'contact@htp.solutions',
    'license': 'OPL-1',
    'depends': ['white_label_kit', 'point_of_sale'],
    'data': [
        'views/pos_receipt_templates.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'white_label_kit_pos/static/src/scss/*.scss',
            'white_label_kit_pos/static/src/xml/*.xml',
            'white_label_kit_pos/static/src/js/*.js',
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
