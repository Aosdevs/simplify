{
    'name': 'Smart Pizza App',
    'version': '17.0.2.0.1',
    'category': 'Sales/Smart Pizza',
    'summary': "A module that helps manage a pizzeria.",
    'description': """
    The module was created as a course work after completing 
    the Odoo school basic course for developers.
    """,
    'author': 'Serhii Sorokin',
    'support': 'sergmagpie@gmail.com',
    'depends': [
        'hr',
        'contacts',
        'pos_restaurant',
        'sale_management',
    ],
    'data': [
        'data/ir_sequence_data.xml',
        'security/smart_pizza_security.xml',
        'security/ir.model.access.csv',
        'data/smart_pizza_data.xml',
        'views/menu.xml',
        'views/hr_delivery_man.xml',
        'views/courier_payment_report.xml',
        'views/courier_shift_views.xml',
        'views/courier_delivery_order.xml',
        'views/restaurant_table.xml',
        'wizard/set_up_delivery_team_wizard.xml',
        'wizard/courier_payment_report_wizard.xml',
    ],
    'demo': [
        'demo/smart_pizza_demo.xml',
    ],
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
