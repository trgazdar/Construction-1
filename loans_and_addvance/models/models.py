# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError, ValidationError


class LoansAndAddvance(models.Model):
    _name = 'loans'
    _description = 'loans_Description'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    @api.model
    def get_journal(self):
        journal = self.env['account.journal'].sudo().search([('is_loan', '=', True)], limit=1).id
        return journal

    state = fields.Selection([("draft", "Draft"),
                              ("financial_manager", "Financial Manager"),
                              ("general_manager", "General Manager"),
                              ("confirm", "Confirmed"),
                              ("paid", "Paid"),
                              ("rejected", "Rejected")],
                             readonly=True,
                             default="draft",
                             tracking=True)
    name = fields.Char('', readonly=True, copy=False, default='New', tracking=True)
    date = fields.Date("Date", tracking=True, required=True)
    deduction_date = fields.Date("Deduction Date", tracking=True, required=True)
    employee_id = fields.Many2one(comodel_name='hr.employee', string="Employee", required=True, tracking=True)
    amount = fields.Float(string="Amount", tracking=True, required=True)
    no_of_installment = fields.Integer(string="No Of Installment", tracking=True, default=1)
    department_id = fields.Many2one(comodel_name="hr.department", string="Department",
                                    related='employee_id.department_id')
    loans_ids = fields.One2many('loans.line', 'loans_id', string="", readonly=True)
    # reason = fields.Text(string="Reason", tracking=True)
    journal_id = fields.Many2one('account.journal', string='Journal', default=get_journal)
    account_id = fields.Many2one('account.account', string='Debit Account', compute='git_account_id_idd')
    account_idd = fields.Many2one('account.account', string='Credit Account', compute='git_account_id_idd')
    loan_id = fields.Many2one('hr.payslip', string='')
    journal_entry_id = fields.Many2one('account.move', string='', copy=False, readonly=True)

    def unlink(self):
        error_message = _('You cannot delete a loans which is in %s state')
        state_description_values = {elem[0]: elem[1] for elem in self._fields['state']._description_selection(self.env)}

        if self.user_has_groups('base.group_user'):
            if any(hol.state not in ['draft', 'rejected'] for hol in self):
                raise UserError(error_message % state_description_values.get(self[:1].state))
        return super(LoansAndAddvance, self).unlink()

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('loans.loane') or 'New'
        result = super(LoansAndAddvance, self).create(vals)
        return result

    @api.depends('journal_id')
    def git_account_id_idd(self):
        for rec in self:
            rec.account_id = False
            rec.account_idd = False
            if rec.journal_id.account_ids and rec.journal_id.account_idd:
                print('rec.journal_id.account_ids.id', rec.journal_id.account_ids.id)
                rec.account_id = rec.journal_id.account_ids.id
                rec.account_idd = rec.journal_id.account_idd.id
            else:
                print("yyyyyyyyyyyyyyyyyyy")
                rec.account_id = False
                rec.account_idd = False

    def compute_installment(self):
        for rec in self:
            loan_line = []
            no_install = rec.no_of_installment
            rec.loans_ids = False
            date_date = rec.deduction_date
            for line in range(no_install):
                loan_line.append((0, 0, {
                    'name': date_date,
                    'amount': rec.amount / rec.no_of_installment,
                }))
                date_date = date_date + relativedelta(months=1)
                print("date_date", date_date)
            rec.loans_ids = loan_line

    def validate_action(self):
        for rec in self:
            rec.state = 'financial_manager'

    def back_to_draft(self):
        for rec in self:
            rec.state = 'draft'

    def financial_manager(self):
        for rec in self:
            rec.state = 'general_manager'

    def general_manager(self):
        for rec in self:
            rec.state = 'confirm'

    def paid(self):
        for rec in self:
            invoice = self.env['account.move'].sudo().create({
                'type': 'entry',
                'ref': rec.name,
                'date': rec.deduction_date,
                'journal_id': self.journal_id.id,
                'line_ids': [(0, 0, {
                    'account_id': rec.account_id.id,
                    # 'partner_id': rec.employee_id.id,
                    'name': rec.employee_id.name,
                    'debit': rec.amount,
                }), (0, 0, {
                    'account_id': rec.account_idd.id,
                    # 'partner_id': rec.employee_id.id,
                    'name': rec.employee_id.name,
                    'credit': rec.amount,
                })],
            })
            rec.journal_entry_id = invoice.id
            rec.state = 'paid'

    def rejected(self):
        for rec in self:
            rec.state = 'rejected'

    # def confirm_action(self):
    #     for rec in self:
    #


# loan model
class LoansAddvanceLine(models.Model):
    _name = 'loans.line'
    _description = 'loans_line'

    loans_payslip_id = fields.Many2one(comodel_name="hr.payslip", string="", required=False, )
    name = fields.Date('Payment Date')
    amount = fields.Float('Amount')
    loans_id = fields.Many2one('loans', string='')


# salary advance model
class EditSalaryAdvance(models.Model):
    _name = 'salary.advance'
    _description = 'salary advance Description'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    @api.model
    def get_journal(self):
        journal = self.env['account.journal'].sudo().search([('is_salary_advance', '=', True)], limit=1).id
        return journal

    state = fields.Selection([("draft", "Draft"),
                              ("financial_manager", "Financial Manager"),
                              ("general_manager", "General Manager"),
                              ("confirm", "Confirmed"),
                              ("paid", "Paid"),
                              ("rejected", "Rejected")],
                             readonly=True,
                             default="draft",
                             tracking=True)
    name = fields.Char('', readonly=True, copy=False, default='New', tracking=True)
    date = fields.Date("Date", tracking=True, required=True)
    deduction_date = fields.Date("Deduction Date", tracking=True, required=True)
    employee_id = fields.Many2one(comodel_name='hr.employee', string="Employee", required=True, tracking=True)
    amount = fields.Float(string="Amount", tracking=True, required=True)
    department_id = fields.Many2one(comodel_name="hr.department", string="Department",
                                    related='employee_id.department_id')
    journal_id = fields.Many2one('account.journal', string='Journal', default=get_journal)
    account_id = fields.Many2one('account.account', string='Debit Account', compute='git_account_id_idd')
    account_idd = fields.Many2one('account.account', string='Credit Account', compute='git_account_id_idd')
    reason = fields.Text(string="Reason", tracking=True)
    salary_advance_id = fields.Many2one('hr.payslip', string='')
    journal_entry_id = fields.Many2one('account.move', string='', copy=False, readonly=True)

    def unlink(self):
        error_message = _('You cannot delete a Advance which is in %s state')
        state_description_values = {elem[0]: elem[1] for elem in self._fields['state']._description_selection(self.env)}

        if self.user_has_groups('base.group_user'):
            if any(hol.state not in ['draft', 'rejected'] for hol in self):
                raise UserError(error_message % state_description_values.get(self[:1].state))
        return super(EditSalaryAdvance, self).unlink()

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('salary.advance') or 'New'
        result = super(EditSalaryAdvance, self).create(vals)
        return result

    @api.depends('journal_id')
    def git_account_id_idd(self):
        for rec in self:
            rec.account_id = False
            rec.account_idd = False
            if rec.journal_id.account_ids and rec.journal_id.account_idd:
                print('rec.journal_id.account_ids.id', rec.journal_id.account_ids.id)
                rec.account_id = rec.journal_id.account_ids.id
                rec.account_idd = rec.journal_id.account_idd.id
            else:
                print("yyyyyyyyyyyyyyyyyyy")
                rec.account_id = False
                rec.account_idd = False

    def validate_action(self):
        for rec in self:
            rec.state = 'financial_manager'

    def back_to_draft(self):
        for rec in self:
            rec.state = 'draft'

    def financial_manager(self):
        for rec in self:
            rec.state = 'general_manager'

    def general_manager(self):
        for rec in self:
            rec.state = 'confirm'

    def paid(self):
        for rec in self:
            invoice = self.env['account.move'].sudo().create({
                'type': 'entry',
                'ref': rec.name,
                'date': rec.deduction_date,
                'journal_id': self.journal_id.id,
                'line_ids': [(0, 0, {
                    'account_id': rec.account_id.id,
                    # 'partner_id': rec.employee_id.id,
                    'name': rec.employee_id.name,
                    'debit': rec.amount,
                }), (0, 0, {
                    'account_id': rec.account_idd.id,
                    # 'partner_id': rec.employee_id.id,
                    'name': rec.employee_id.name,
                    'credit': rec.amount,
                })],
            })
            rec.journal_entry_id = invoice.id
            rec.state = 'paid'

    def rejected(self):
        for rec in self:
            rec.state = 'rejected'


class HrPaysLipInherit(models.Model):
    _inherit = 'hr.payslip'

    loan_ids = fields.One2many(comodel_name="loans", inverse_name="loan_id", string="", required=False, )
    # compute='get_loan_ids')
    loans_line_ids = fields.One2many(comodel_name="loans.line", inverse_name="loans_payslip_id", string="",
                                     required=False,
                                     compute='get_loan_ids')
    loans = fields.Float(string="Loans", compute='get_total_loans')
    salary_advance_ids = fields.One2many(comodel_name="salary.advance", inverse_name="salary_advance_id", string="",
                                         required=False, compute='get_salary_advance_ids')
    salary_advance = fields.Float(string="Salary Advance", compute='get_total_salary_advance')

    @api.depends('employee_id', 'date_from', 'date_to', )
    def get_loan_ids(self):
        self.loan_ids = False
        loans = self.env['loans'].search([
            ('employee_id', '=', self.employee_id.id),
            ('state', '=', 'paid'),
            ('deduction_date', '<=', self.date_to),
            ('deduction_date', '>=', self.date_from),
        ])
        lines_list = []
        for x in loans:
            for y in x.loans_ids:
                if y.name <= self.date_to and y.name >= self.date_from:
                    lines_list.append(y.id)
        if lines_list:
            self.loans_line_ids = lines_list
        # for rec in self:
        #     pass

        else:
            self.loans_line_ids = False

    @api.depends('employee_id', 'date_from', 'date_to', )
    def get_salary_advance_ids(self):
        self.salary_advance_ids = False
        salary_advance = self.env['salary.advance'].search([
            ('employee_id', '=', self.employee_id.id),
            ('state', '=', 'paid'),
            ('deduction_date', '<=', self.date_to),
            ('deduction_date', '>=', self.date_from),
        ])
        if salary_advance:
            for rec in self:
                rec.salary_advance_ids = salary_advance
        else:
            self.salary_advance_ids = False

    @api.depends('employee_id', 'date_from', 'date_to', )
    def get_total_loans(self):
        loan_loan = 0
        for rec in self:
            rec.loans = False
            if rec.loans_line_ids:
                for line in rec.loans_line_ids:
                    loan_loan = loan_loan + line.amount
                rec.loans = loan_loan
            else:
                rec.loans = False

    @api.depends('employee_id', 'date_from', 'date_to', )
    def get_total_salary_advance(self):
        advance = 0
        for rec in self:
            rec.salary_advance = False
            if rec.salary_advance_ids:
                for line in rec.salary_advance_ids:
                    advance = advance + line.amount
                rec.salary_advance = advance
            else:
                rec.salary_advance = False


#
class AccountJournalInherit(models.Model):
    _inherit = 'account.journal'

    is_loan = fields.Boolean(string="Is Loan", )
    is_salary_advance = fields.Boolean(string="Is Salary Advance", )
    account_ids = fields.Many2one('account.account', string='Debit Account', )
    account_idd = fields.Many2one('account.account', string='Credit Account', )

    #
    # def unlink(self):
    #     error_message = _('You cannot delete a time off which is in %s state')
