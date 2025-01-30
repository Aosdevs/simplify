from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CourierShift(models.Model):
    _name = "courier.shift"
    _description = "Courier Shift"

    delivery_man_id = fields.Many2one(
        comodel_name='hr.delivery.man',
        string='Courier',
    )
    time_start = fields.Datetime(
        string='Start Time',
    )
    time_end = fields.Datetime(
        string='End Time',
    )
    active = fields.Boolean(
        default=True,
    )
    status = fields.Selection(
        selection=[
            ('planed', 'Planed'),
            ('happening', 'Happening'),
            ('completed', 'Completed'),
        ],
        default='planed',
    )
    courier_delivery_order_ids = fields.One2many(
        comodel_name='courier.delivery.order',
        inverse_name='courier_shift_id',
    )
    number_delivery_orders = fields.Integer(
        compute='compute_number_delivery_orders',
    )

    def compute_number_delivery_orders(self):
        for record in self:
            record.number_delivery_orders = len(record.courier_delivery_order_ids)

    def _compute_display_name(self):
        for record in self:
            record.display_name = (f"{record.delivery_man_id.user_id.display_name}"
                                   f"{record.time_start and record.time_start.strftime(' %d %b') or ''}")

    @api.constrains('delivery_man_id', 'time_start', 'time_end')
    def _check_unique_shift(self):
        for shift in self:
            if shift.time_end < shift.time_start:
                raise ValidationError(_('The End Time cannot be earlier than the Start Time!'))
            if self.search_count([('delivery_man_id', '=', shift.delivery_man_id.id),
                                  ('time_start', '<=', shift.time_end),
                                  ('time_end', '>=', shift.time_start)]) > 1:
                raise ValidationError(_("Couriers' work shifts cannot coincide!"))

    def action_delivery_orders_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('smart_pizza.courier_delivery_order_act_window')
        action['domain'] = [('courier_shift_id', '=', self.id)]
        return action

    def apply_to_restaurant(self):
        self.ensure_one()
        if not (self.time_start <= fields.Datetime.now() <= self.time_end):
            raise ValidationError(_("You need to correct the shift time!"))
        delivery_floor_id = self.env.ref('smart_pizza.floor_delivery_team', raise_if_not_found=False)
        if not delivery_floor_id:
            raise ValidationError(_("The delivery functionality is not configured, contact the administrator!"))
        if self.id not in delivery_floor_id.table_ids.courier_shift_id.ids:
            count = len(delivery_floor_id.table_ids)
            delivery_floor_id.table_ids.create([{
                'name': self.delivery_man_id.display_name,
                'floor_id': delivery_floor_id.id,
                'position_v': 10 + count * 60,
                'width': 300,
                'courier_shift_id': self.id,
            }])
        self.status = 'happening'
