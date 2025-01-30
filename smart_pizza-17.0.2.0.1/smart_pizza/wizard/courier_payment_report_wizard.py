from odoo import fields, models, api
from odoo.tools.date_utils import start_of, end_of


class CourierPaymentReportWizard(models.TransientModel):
    _name = "courier.payment.report.wizard"
    _description = "Courier Payment Report Wizard"

    delivery_man_ids = fields.Many2many(
        comodel_name='hr.delivery.man',
        relation="delivery_man_rel",
        string='Delivery Man',
        default=lambda self: self.env.context.get('active_ids', []),
    )
    from_date = fields.Date(
        string='From Date',
        default=lambda self: start_of(fields.Date.today(), 'month'),
    )
    to_date = fields.Date(
        string='To Date',
        default=lambda self: end_of(fields.Date.today(), 'month'),
    )
    delivery_order_ids = fields.Many2many(
        comodel_name='courier.delivery.order',
        relation='delivery_order_rel',
        string='Courier Delivery Order',
    )

    @api.onchange('delivery_man_ids', 'from_date', 'to_date')
    def onchange_for_delivery_order_ids(self):
        """necessary method for hospital"""
        search_domain = []
        if self.delivery_man_ids:
            search_domain.append(('delivery_man_id', 'in', self.delivery_man_ids.ids))
        if self.from_date:
            search_domain.append(('time_start', '>=', self.from_date))
        if self.to_date:
            search_domain.append(('time_start', '<=', self.to_date))
        self.delivery_order_ids = [(6, 0, self.delivery_order_ids.search(search_domain).ids)]

    def courier_payment_report(self):
        """necessary method for hospital"""
        data = {
            'from_date': self.from_date,
            'to_date': self.to_date,
            'lines': [{
                'delivery_order': line.name,
                'total': line.amount_total,
                'delivery_cost': line.delivery_cost,
                'status': line.state,
            } for line in self.delivery_order_ids],
            'number_of_orders': len(self.delivery_order_ids),
            'total_of_orders': sum(line.amount_total for line in self.delivery_order_ids),
            'total_salary': sum(line.delivery_cost for line in self.delivery_order_ids),
            'paid_salary': sum(
                line.delivery_cost for line in self.delivery_order_ids.filtered(lambda line: line.state == 'paid')),
        }
        res = self.env.ref('smart_pizza.action_courier_payment_report').report_action(self.delivery_man_ids.ids,
                                                                                      data=data)
        return res
