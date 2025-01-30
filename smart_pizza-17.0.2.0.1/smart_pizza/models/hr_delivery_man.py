from odoo import fields, models


class HrDeliveryMan(models.Model):
    _name = "hr.delivery.man"
    _inherits = {'hr.employee': 'employee_id'}
    _description = "Hr Delivery Man"

    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        required=True,
        ondelete='restrict',
        auto_join=True,
        index=True,
        string='Related Employee',
        help='Employee-related data of the user',
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='User',
        related='employee_id.user_id',
        ondelete='restrict',
    )
    delivery_order_ids = fields.One2many(
        comodel_name='courier.delivery.order',
        inverse_name='delivery_man_id',
    )
    profit = fields.Float(
        string='Profit',
        compute='_compute_profit',
    )

    def _compute_profit(self):
        for record in self:
            record.profit = sum(
                record.delivery_order_ids.filtered(lambda order: order.state == 'done').mapped('delivery_cost'))

    def pay_profit(self):
        self.ensure_one()
        self.delivery_order_ids.filtered(lambda order: order.state == 'done').write({
            'state': 'paid',
            'date_paid': fields.Datetime.now(),
        })

    def action_delivery_orders_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('smart_pizza.courier_delivery_order_act_window')
        action['domain'] = [('delivery_man_id', '=', self.id)]
        return action
