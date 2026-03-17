from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, values):
        # Add code here
        return super().create(values)