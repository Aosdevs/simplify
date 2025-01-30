from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CourierDeliveryOrder(models.Model):
    _name = "courier.delivery.order"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Courier Delivery Order"

    name = fields.Char(
        string="Courier Delivery Order",
        required=True,
        copy=False,
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Customer",
        required=True,
        tracking=1,
    )
    state = fields.Selection(
        selection=[
            ('draft', "Draft"),
            ('in_progress', "In progress"),
            ('done', "Done"),
            ('paid', "Paid"),
            ('cancel', "Cancelled"),
        ],
        string="Status",
        readonly=True,
        copy=False,
        tracking=3,
        default='draft',
    )
    courier_shift_id = fields.Many2one(
        comodel_name='courier.shift',
        string="Courier Shift",
        copy=False,
        tracking=4,
    )
    delivery_man_id = fields.Many2one(
        comodel_name='hr.delivery.man',
        string="Delivery Man",
        copy=False,
        required=False,
        tracking=2,
    )
    pos_order_id = fields.Many2one(
        comodel_name='pos.order',
    )
    amount_total = fields.Float(
        related='pos_order_id.amount_total',
        string='Total',
        digits=0,
        readonly=True,
        required=True,
    )
    delivery_cost = fields.Float(
        compute='compute_delivery_cost',
    )
    time_start = fields.Datetime(
        string='Start Time',
        readonly=True,
    )
    time_end = fields.Datetime(
        string='End Time',
        readonly=True,
    )
    date_paid = fields.Datetime(
        string='Paid Date',
        readonly=True,
    )

    def compute_delivery_cost(self):
        delivery_pos_category_id = self.env.ref('smart_pizza.delivery_pos_category')
        for record in self:
            record.delivery_cost = sum(record.pos_order_id.lines.filtered(
                lambda line: delivery_pos_category_id in line.product_id.pos_categ_ids).mapped('price_subtotal_incl'))

    def took_the_order(self):
        self.ensure_one()
        vals = {
            'state': 'in_progress',
            'time_start': fields.Datetime.now(),
        }
        if not self.delivery_man_id:
            delivery_man_id = self.env['hr.delivery.man'].search([
                ('user_id', '=', self.env.user.id),
            ], limit=1)
            if not delivery_man_id:
                raise ValidationError(_('You need to select a delivery man!'))
            vals['delivery_man_id'] = delivery_man_id.id
        self.update(vals)

    def cancel_the_order(self):
        self.ensure_one()
        self.update({'state': 'cancel'})

    def done_the_order(self):
        self.ensure_one()
        if self.pos_order_id.state in ('draft', 'cancel'):
            raise ValidationError(_('Return the money to the cashier!'))
        else:
            self.update({
                'state': 'done',
                'time_end': fields.Datetime.now(),
            })
            if not self.time_start:
                self.time_start = fields.Datetime.now()
