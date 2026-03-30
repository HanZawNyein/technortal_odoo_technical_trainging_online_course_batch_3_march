from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HMSRoomOrder(models.Model):
    _name = "hms.room.order"
    _description = "HMS Room Order"

    name = fields.Char(default=lambda self: _("New"), readonly=True)  # one line
    room_type_id = fields.Many2one('hms.room.type', required=True)
    room_id = fields.Many2one('hms.room', required=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    amount = fields.Monetary(currency_field='currency_id')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('cancelled', 'Cancelled'),
    ], default='draft')
    extra_qty = fields.Integer('Extra')
    extra_per_fees = fields.Monetary(currency_field='currency_id')
    total_extra_fees = fields.Monetary(currency_field='currency_id')
    total_amount = fields.Monetary(currency_field='currency_id', compute='_compute_total_amount')
    invoice_ids = fields.Many2many('account.move',copy=False)
    invoice_count = fields.Integer(compute="_compute_invoice_count")

    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        for record in self:
            record.invoice_count = len(record.invoice_ids)

    @api.constrains('extra_qty')
    def _check_extra_qty(self):
        if self.extra_qty > self.room_id.allowed_extra_person:
            raise ValidationError(_(f'{self.room_id.allowed_extra_person} persons only Allow for Extra.'))

    @api.onchange('room_id')
    def _onchange_room_id(self):
        if self.room_id:
            self.amount = self.room_id.amount
            self.extra_per_fees = self.room_id.extra_per_fees

    @api.onchange('extra_qty', 'extra_per_fees')
    def _onchange_extra_qty(self):
        if self.extra_qty and self.extra_per_fees:
            self.total_extra_fees = self.extra_per_fees * self.extra_qty

    @api.depends('total_amount', 'total_extra_fees')
    def _compute_total_amount(self):
        self.total_amount = self.amount + self.total_extra_fees

    def action_draft(self):
        self.state = 'draft'

    def action_confirmed(self):
        self.state = 'confirmed'
        if self.name == _("New"):
            self.name = self.env['ir.sequence'].next_by_code('hms.room.order')
        # return self.action_create_invoice()

    def action_paid(self):
        for record in self:
            record.state = 'paid'

    def action_check_in(self):
        self.state = 'checked_in'

    def action_check_out(self):
        self.state = 'checked_out'

    def action_cancel(self):
        self.state = 'cancelled'

    def action_create_invoice(self):
        data = {'auto_post': 'no', 'auto_post_until': False,
                'campaign_id': False, 'checked': False,
                'company_id': self.company_id.id,
                'currency_id': self.currency_id.id,
                'date': fields.Date.today(),
                'delivery_date': False,
                'fiscal_position_id': 1,
                'incoterm_location': False,
                'invoice_currency_rate': 1,
                'invoice_date': fields.Date.today(),
                'invoice_date_due': fields.Date.today(),
                'invoice_incoterm_id': False,
                'invoice_line_ids': [[0, 0,
                                      {'account_id': 26,
                                       'collapse_composition': False,
                                       'collapse_prices': False,
                                       'currency_id': 1,
                                       'deductible_amount': 100,
                                       'discount': 0,
                                       'display_type': 'product',
                                       'is_downpayment': False,
                                       # 'name': '[CONS_0001] Whiteboard Pen',
                                       'partner_id': 15,
                                       'price_unit': self.amount,
                                       'product_id': self.room_id.product_id.id,
                                       'product_uom_id': 1,
                                       'purchase_line_id': False,
                                       'quantity': 1,
                                       'sequence': 100,
                                       'tax_ids': []}],
                                     [0, 0,
                                      {'account_id': 26,
                                       'collapse_composition': False,
                                       'collapse_prices': False,
                                       'currency_id': 1,
                                       'deductible_amount': 100,
                                       'discount': 0,
                                       'display_type': 'product',
                                       'is_downpayment': False,
                                       'name': 'Extra Persons',
                                       'partner_id': 15,
                                       'price_unit': self.extra_per_fees,
                                       'product_id': 26,
                                       'product_uom_id': 1,
                                       'purchase_line_id': False,
                                       'quantity': self.extra_qty,
                                       'sequence': 101,
                                       'tax_ids': []}]],
                'invoice_origin': False, 'invoice_payment_term_id': 6, 'invoice_source_email': False,
                'invoice_user_id': 1, 'journal_id': 1, 'medium_id': False, 'move_type': 'out_invoice', 'name': False,
                'narration': '<p>Terms &amp; Conditions: http://localhost:8069/terms</p>', 'origin_payment_id': False,
                'partner_bank_id': False, 'partner_id': 15, 'partner_shipping_id': 15, 'payment_reference': False,
                'payment_state': 'not_paid', 'posted_before': False, 'preferred_payment_method_line_id': False,
                'purchase_id': False, 'purchase_vendor_bill_id': False, 'qr_code_method': False,
                'quick_edit_total_amount': 0, 'ref': False, 'show_name_warning': False, 'show_update_fpos': False,
                'source_id': False, 'statement_line_id': False, 'tax_cash_basis_created_move_ids': [],
                'taxable_supply_date': False, 'team_id': 1, 'user_id': 1}
        move_id = self.env['account.move'].create(data)
        self.invoice_ids += move_id
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "res_id": move_id.id,
            "view_mode": "form"
        }

    def action_view_invoices(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            # "res_id": move_id.id,
            "view_mode": "list,form",
            "domain":[('id','in',self.invoice_ids.ids)],
        }
