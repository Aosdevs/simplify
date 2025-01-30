from odoo import fields, models


class RestaurantTable(models.Model):
    _inherit = 'restaurant.table'

    courier_shift_id = fields.Many2one(
        comodel_name='courier.shift',
    )
