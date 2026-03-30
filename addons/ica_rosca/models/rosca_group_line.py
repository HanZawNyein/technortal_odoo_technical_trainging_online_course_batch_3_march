from odoo import api, fields, models

class RoscaGroupLine(models.Model):
    _name = 'rosca.group.line'
    _description = 'RoscaGroupLine'

    group_id = fields.Many2one('rosca.group')
    partner_id = fields.Many2one('res.partner',required=True)
    draw_number = fields.Integer()
    payout_date = fields.Date()