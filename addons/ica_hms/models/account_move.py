from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    # @api.model
    # def create(self, values):
    #     # Add code here
    #     return super().create(values)

    # def action_post(self):
    #     res= super().action_post()
    #     orders = self.env['hms.room.order'].browse(self.ids)
    #     orders.action_paid()
    #     return res
