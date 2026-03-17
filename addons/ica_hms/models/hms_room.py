from odoo import api, fields, models


class HMSRoom(models.Model):
    _name = "hms.room"
    _description = "HMS Room"

    name = fields.Char(required=True)  # one line
    state = fields.Selection(
        [('draft', 'Draft'),
         ('available', 'Available'),
         ('not_available', 'Not Available')], default='draft')
    type = fields.Many2one('hms.room.type', required=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    amount = fields.Monetary(currency_field='currency_id')
    extra_per_fees = fields.Monetary(currency_field='currency_id')
    allowed_extra_person = fields.Integer()
    product_id = fields.Many2one('product.product', required=True)

    @api.onchange('type')
    def _onchange_room_type(self):
        if self.type:
            self.company_id = self.type.company_id
            self.amount = self.type.amount
