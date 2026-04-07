from datetime import timedelta

from odoo import fields, models,_
import random


class RoscaGroup(models.Model):
    _name = 'rosca.group'
    _description = 'RoscaGroup'

    name = fields.Char(required=True, copy=False, default=lambda self: _("New"),readonly=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=False, readonly=True, copy=False)
    partner_ids = fields.Many2many('res.partner')
    line_ids = fields.One2many('rosca.group.line', 'group_id')
    state = fields.Selection([
        ('draft', 'draft'),
        ('locked', "locked"),
        ('lucky_draw', 'Lucky Draw')
    ], default='draft')
    duration_days = fields.Integer(default=1)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    per_amount = fields.Monetary(currency_field='currency_id')

    def action_draft(self):
        self.state = 'draft'

    def action_locked(self):
        self.state = 'locked'

    def action_lucky_draw(self):
        self.line_ids.unlink()
        self._create_sequence()
        partners = self.partner_ids
        total = len(partners)

        # Generate unique numbers
        numbers = random.sample(range(1, total + 1), total)

        data = []
        for partner, num in zip(partners, numbers):
            data.append((0, 0, {
                'draw_number': num,
                'reference':f"{self.name}-{num}",
                'partner_id': partner.id,
            }))

        self.line_ids = data
        self._action_payout_date()
        self.line_ids.action_generate_payout_line()
        self.state = 'lucky_draw'

    def _action_payout_date(self):
        payout_date = self.start_date
        for line_id in self.line_ids.sorted('draw_number'):
            payout_date += timedelta(days=self.duration_days)
            line_id.payout_date = payout_date
            if self.line_ids.sorted('draw_number')[-1] == line_id:
                self.end_date = payout_date

    def action_unlock(self):
        self.state = 'draft'

    def _create_sequence(self):
        if self.name == _("New"):
            rg_sequence = self.env['ir.sequence'].next_by_code('rosca.group')
            self.name = rg_sequence