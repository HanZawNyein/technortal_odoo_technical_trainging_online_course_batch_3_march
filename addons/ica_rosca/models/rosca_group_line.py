from odoo import api, fields, models

class RoscaGroupLine(models.Model):
    _name = 'rosca.group.line'
    _description = 'RoscaGroupLine'
    _rec_name = 'partner_id'

    group_id = fields.Many2one('rosca.group')
    partner_id = fields.Many2one('res.partner',required=True)
    draw_number = fields.Integer()
    payout_date = fields.Date()

    def action_view(self):
        return {
            "name":f"{self.group_id.name}'s rosca line",
            "type": "ir.actions.act_window",
            "res_model": "rosca.group.line",
            "res_id": self.id,
            "view_mode": "form",
        }