# -*- coding: utf-8 -*-
import time
import babel
from odoo import models, fields, api, tools, _
from datetime import datetime


class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    loan_line_id = fields.Many2one('hr.loan.line', string="Loan Installment", help="Loan installment")


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from', 'date_to')
    def _onchange_employee(self):
        res = super()._onchange_employee()
        loan_type = self.env.ref('ohrms_loan.hr_rule_input_loan', raise_if_not_found=False)
        amount = 0.0
        loan_line_id = False
        for payslip in self:
            loans = self.env['hr.loan'].search([('employee_id', '=', payslip.employee_id.id),('state', '=', 'approve')])
            for line in loans.loan_lines:
                amount = line.amount
                loan_line_id = line.id
            if not loan_type:
                payslip.input_line_ids = payslip.input_line_ids
                continue
            lines_to_keep = payslip.input_line_ids.filtered(lambda x: x.input_type_id != loan_type)
            input_lines_vals = [(5, 0, 0)] + [(4, line.id, False) for line in lines_to_keep]
            input_lines_vals.append((0, 0, {
                'amount': amount,
                'input_type_id': loan_type.id,
                'loan_line_id' : loan_line_id
            }))
            payslip.update({'input_line_ids': input_lines_vals})
            return res

    def action_payslip_done(self):
        for line in self.input_line_ids:
            if line.loan_line_id:
                line.loan_line_id.paid = True
                line.loan_line_id.loan_id._compute_loan_amount()
        return super(HrPayslip, self).action_payslip_done()
