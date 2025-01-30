from odoo import models


class PosConfig(models.Model):
    _inherit = "pos.config"

    def open_ui(self):
        if not self._context.get('team_approved') and not self.current_session_id:
            action = self.env['ir.actions.act_window']._for_xml_id('smart_pizza.setup_delivery_team_wizard_act_window')
            action['context'] = {
                'default_pos_config_id': self.id,
            }
            return action
        res = super().open_ui()
        return res
