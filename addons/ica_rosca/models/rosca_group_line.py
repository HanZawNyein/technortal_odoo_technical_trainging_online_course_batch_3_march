from odoo import api, fields, models


class RoscaGroupLine(models.Model):
    _name = 'rosca.group.line'
    _description = 'RoscaGroupLine'
    _rec_name = 'reference'

    group_id = fields.Many2one('rosca.group')
    partner_ids = fields.Many2many('res.partner', related="group_id.partner_ids", string="Rosca Groups")
    partner_id = fields.Many2one('res.partner', required=True, string="Owner")
    draw_number = fields.Integer()
    reference = fields.Char()
    payout_date = fields.Date()
    payout_line_ids = fields.One2many('rosca.payout.line', 'line_id', string="Payout Lines")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    total_amount = fields.Monetary(currency_field='currency_id',compute="_compute_total_amount")
    paid_amount = fields.Monetary(currency_field='currency_id',compute="_compute_paid_amount")
    remaining_amount = fields.Monetary(currency_field='currency_id',compute="_compute_remaining_amount")

    @api.depends('payout_line_ids')
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount = sum(rec.payout_line_ids.mapped('amount'))

    @api.depends('payout_line_ids')
    def _compute_paid_amount(self):
        for rec in self:
            rec.paid_amount = sum(rec.payout_line_ids.filtered('is_paid').mapped('amount'))

    @api.depends('paid_amount','total_amount')
    def _compute_remaining_amount(self):
        for rec in self:
            rec.remaining_amount = rec.total_amount-rec.paid_amount

    def action_view(self):
        return {
            "name": f"{self.group_id.name}'s rosca line",
            "type": "ir.actions.act_window",
            "res_model": "rosca.group.line",
            "res_id": self.id,
            "view_mode": "form",
        }

    def action_generate_payout_line(self):
        for rec in self:
            payout_line_ids = rec.payout_line_ids._prepare_payout_line(line_id=rec)
            rec.payout_line_ids = payout_line_ids
