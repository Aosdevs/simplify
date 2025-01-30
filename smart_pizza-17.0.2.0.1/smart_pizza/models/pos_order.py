from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for pos_order_id in res:
            if pos_order_id.table_id.courier_shift_id:
                if not pos_order_id.partner_id:
                    raise ValidationError(_('Customer required!'))
                if self.env.ref('smart_pizza.delivery_pos_category') not in pos_order_id.lines.product_id.pos_categ_ids:
                    raise ValidationError(_('Delivery required!'))
                self.env['courier.delivery.order'].create([{
                    'name': self.env['ir.sequence'].next_by_code('courier.delivery.order') or _('New'),
                    'partner_id': pos_order_id.partner_id.id,
                    'state': 'draft',
                    'courier_shift_id': pos_order_id.table_id.courier_shift_id.id,
                    'delivery_man_id': pos_order_id.table_id.courier_shift_id.delivery_man_id.id,
                    'pos_order_id': pos_order_id.id,
                }])
        return res

    def write(self, vals):
        if 'state' in vals and vals['state'] == 'paid':
            courier_delivery_order_id = self.env['courier.delivery.order'].search([('pos_order_id', 'in', self.ids)])
            if courier_delivery_order_id:
                values = {
                    'state': 'done',
                    'time_end': fields.Datetime.now(),
                }
                if not courier_delivery_order_id.time_start:
                    values.update({'time_start': fields.Datetime.now()})
                courier_delivery_order_id.update(values)
        res = super().write(vals)
        return res
