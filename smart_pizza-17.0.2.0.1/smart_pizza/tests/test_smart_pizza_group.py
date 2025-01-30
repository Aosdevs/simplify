from odoo.addons.smart_pizza.tests.common import SmartPizzaCommon
from odoo.tests import tagged, users
from odoo.exceptions import AccessError


@tagged('post_install', '-at_install')
class TestAccessRights(SmartPizzaCommon):
    """My amazing test case."""

    @users('delivery_user')
    def test_access_delivery_user(self):
        """just method for testing some test cases"""
        with self.assertRaises(AccessError):
            self.courier_shift_1.write({
                'status': 'happening'
            })

    @users('administrator_user')
    def test_access_administrator_user(self):
        """just method for testing some test cases"""
        self.assertTrue(self.courier_shift_1.write({
            'status': 'happening'
        }))
