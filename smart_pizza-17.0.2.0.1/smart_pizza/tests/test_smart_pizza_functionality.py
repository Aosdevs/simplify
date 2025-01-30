from odoo.addons.smart_pizza.tests.common import SmartPizzaCommon
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestSmartPizzaFunctionality(SmartPizzaCommon):
    """My amazing test case."""

    @classmethod
    def setUpClass(cls):
        """class method for setting up the test case"""
        super(TestSmartPizzaFunctionality, cls).setUpClass()
        cls.test_courier_delivery_order = cls.env['courier.delivery.order'].create({
            'name': 'Courier Delivery Order',
            'partner_id': cls.env.ref('base.res_partner_1'),
            'courier_shift_id': cls.courier_shift_1,
            'delivery_man_id': cls.delivery_man,
            'state': 'done',
        })

    def test_compute_number_delivery_orders(self):
        """just method for testing some test cases"""
        self.assertEqual(self.courier_shift_1.number_delivery_orders, 1)
