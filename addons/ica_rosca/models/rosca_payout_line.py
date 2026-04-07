from odoo import api, fields, models, _


class RoscaPayoutLine(models.Model):
    _name = 'rosca.payout.line'
    _description = 'RoscaPayoutLine'

    name = fields.Char(readonly=True, default=lambda self: _('New'), copy=False)
    line_id = fields.Many2one('rosca.group.line')
    group_id = fields.Many2one('rosca.group', related='line_id.group_id')
    partner_id = fields.Many2one('res.partner', string="Source")
    dest_partner_id = fields.Many2one('res.partner', string="Destination")
    payout_date = fields.Date()
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    amount = fields.Monetary(currency_field='currency_id')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('late', 'Late'),
        ('cancel', 'Cancel'),
    ], default='draft', compute="_compute_state")
    is_paid = fields.Boolean(default=False)

    def action_paid(self):
        self.is_paid = True
        # self._compute_state()

    @api.depends('payout_date')
    def _compute_state(self):
        for payout_line in self:
            if payout_line.is_paid:
                payout_line.state = 'paid'
            elif payout_line.payout_date == fields.Date.today():
                payout_line.state = 'unpaid'
            elif payout_line.payout_date < fields.Date.today():
                payout_line.state = 'late'
            else:
                payout_line.state = 'draft'

    def _prepare_payout_line(self, line_id):
        # partner_ids = group_id.partner_ids
        group_id = line_id.group_id
        partner_ids = group_id.partner_ids
        data = []
        owner_id = line_id.partner_id
        if partner_ids:
            dest_partner_ids = partner_ids - owner_id
            amount = group_id.per_amount
            payout_date = line_id.payout_date
            for partner in dest_partner_ids:
                data.append((0, 0, {
                    'line_id': line_id.id,
                    'group_id': group_id.id,
                    'partner_id': owner_id.id,
                    'dest_partner_id': partner.id,
                    "company_id": group_id.company_id.id,
                    "amount": amount,
                    "payout_date": payout_date,
                }))
        return data

    @api.model
    def create(self, values):
        # Add code here
        for val in values:
            if val.get('name', _("New")) == _("New"):
                val['name'] = self.env['ir.sequence'].next_by_code('rosca.payout.line')
        return super(RoscaPayoutLine, self).create(values)
