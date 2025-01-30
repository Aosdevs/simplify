from datetime import datetime, timedelta

from odoo.tests import TransactionCase
from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class SmartPizzaCommon(TransactionCase):
    """My amazing test case."""

    @classmethod
    def setUpClass(cls):
        """class method for setting up the test case"""
        super().setUpClass()

        cls.env = cls.env['base'].with_context(**DISABLED_MAIL_CONTEXT).env

        cls.group_kitchen = cls.env.ref('smart_pizza.group_kitchen')
        cls.group_delivery = cls.env.ref('smart_pizza.group_delivery')
        cls.group_waiter = cls.env.ref('smart_pizza.group_waiter')
        cls.group_administrator = cls.env.ref('smart_pizza.group_administrator')

        cls.kitchen_user = cls.env['res.users'].create({
            'name': 'Test Kitchen',
            'login': 'kitchen_user',
            'password': 'kitchen_user',
            'email': 'kitchen_user@example.com',
            'groups_id': [(6, 0, cls.group_kitchen.ids)],
        })
        cls.delivery_user = cls.env['res.users'].create({
            'name': 'Test Delivery',
            'login': 'delivery_user',
            'password': 'delivery_user',
            'email': 'delivery_user@example.com',
            'groups_id': [(6, 0, cls.group_delivery.ids)],
        })
        cls.waiter_user = cls.env['res.users'].create({
            'name': 'Test Waiter',
            'login': 'waiter_user',
            'password': 'waiter_user',
            'email': 'waiter_user@example.com',
            'groups_id': [(6, 0, cls.group_waiter.ids)],
        })
        cls.administrator_user = cls.env['res.users'].create({
            'name': 'Test Administrator',
            'login': 'administrator_user',
            'password': 'administrator_user',
            'email': 'administrator_user@example.com',
            'groups_id': [(6, 0, cls.group_administrator.ids)],
        })
        cls.delivery_man = cls.env['hr.delivery.man'].create({
            'user_id': cls.delivery_user.user_id.id,
        })
        cls.administrator = cls.env['hr.delivery.man'].create({
            'user_id': cls.administrator_user.user_id.id,
        })
        cls.courier_shift_1 = cls.env['courier.shift'].create({
            'delivery_man_id': cls.delivery_man.id,
            'time_start': datetime.now() - timedelta(minutes=60),
            'time_end': datetime.now() + timedelta(minutes=60),
        })
