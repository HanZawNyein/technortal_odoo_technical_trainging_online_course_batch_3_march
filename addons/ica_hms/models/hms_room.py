from odoo import api, fields, models


class HMSRoom(models.Model):
    _name = "hms.room"
    _description = "HMS Room"

    name = fields.Char(required=True)  # one line
    state = fields.Selection(
        [('draft', 'Draft'),
         ('available', 'Available'),
         ('not_available', 'Not Available')],
        default='draft')
