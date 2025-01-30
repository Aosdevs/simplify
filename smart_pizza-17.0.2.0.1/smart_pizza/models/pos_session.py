from odoo import models


class PosSession(models.Model):
    _inherit = "pos.session"

    def action_pos_session_close(self, balancing_account=False, amount_to_balance=0, bank_payment_method_diffs=None):
        res = super().action_pos_session_close(balancing_account, amount_to_balance, bank_payment_method_diffs)
        if res and self.state == 'closed':
            self.config_id.floor_ids.table_ids.courier_shift_id.write({
                'status': 'completed',
            })
        return res
