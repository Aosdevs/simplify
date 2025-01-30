from odoo import fields, models, _
from odoo.exceptions import UserError


class SetupDeliveryTeamWizard(models.TransientModel):
    _name = "setup.delivery.team.wizard"
    _description = "Setup delivery team wizard"

    pos_config_id = fields.Many2one(
        comodel_name='pos.config',
    )
    delivery_floor_id = fields.Many2one(
        comodel_name='restaurant.floor',
        string="Delivery Floor",
        default=lambda self: self.env.ref('smart_pizza.floor_delivery_team', raise_if_not_found=False).id,
    )
    courier_shift_ids = fields.Many2many(
        comodel_name='courier.shift',
        default=lambda self: self._default_courier_shift_ids(),
    )

    def _default_courier_shift_ids(self):
        return self.courier_shift_ids.search([
            ('time_start', '<=', fields.Datetime.now()),
            ('time_end', '>=', fields.Datetime.now())
        ])

    def action_approve(self):
        if self.courier_shift_ids - self._default_courier_shift_ids():
            raise UserError(_("Sorry, but courier shifts out of times."))
        self.delivery_floor_id.table_ids.unlink()
        self.delivery_floor_id.table_ids.create([{
            'name': courier_shift_id.delivery_man_id.display_name,
            'floor_id': self.delivery_floor_id.id,
            'position_v': 10 + count * 60,
            'width': 300,
            'courier_shift_id': courier_shift_id.id,
        } for count, courier_shift_id in enumerate(self.courier_shift_ids)])
        self.courier_shift_ids.write({'status': 'happening'})
        return self.pos_config_id.with_context(team_approved=True).open_ui()
