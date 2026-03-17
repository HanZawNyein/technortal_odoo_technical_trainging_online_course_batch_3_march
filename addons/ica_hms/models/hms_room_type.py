from odoo import api, fields, models


class HMSRoomType(models.Model):
    _name = "hms.room.type"
    _description = "HMS Room Type"

    name = fields.Char(required=True)  # one line
    company_id = fields.Many2one('res.company',default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency',related='company_id.currency_id')
    amount = fields.Monetary(currency_field='currency_id')