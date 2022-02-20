# -*- coding: utf-8 -*-

from odoo import models, fields, api


class NumberUnit(models.Model):
    _name = 'number.unit'
    _description = 'Number Unit'

    name = fields.Char(string="Name", )
    id = fields.Integer(string="ID", required=False, )


class EditHrEmployee(models.Model):
    _inherit = 'hr.employee'

    batch_id = fields.Many2one(comodel_name="batch.payslip", string="", required=False, )
    number_unit_id = fields.Many2one(comodel_name="number.unit", string="Number Unit", required=False, )


class BatchPayslip(models.Model):
    _name = 'batch.payslip'
    _description = 'New Description'

    name = fields.Char('Batch Name')
    date_from = fields.Date(string="Date From", required=False, )
    date_to = fields.Date(string="Date to", required=False, )
    struct_id = fields.Many2one('hr.payroll.structure', string='Salary Structure')

    batch_ids = fields.One2many(comodel_name="hr.employee", inverse_name="batch_id", string="employees", copy=False,
                                required=False)
    payslibs_ids = fields.Many2many(comodel_name="hr.payslip", string="employees", copy=False,
                                    required=False)
    company_id = fields.Many2one('res.company', string='Company', )
    number_unit_id = fields.Many2one(comodel_name="number.unit", string="Number Unit", required=False, )
    state = fields.Selection(string="", selection=[('draft', 'Draft'), ('wait', 'Waiting'), ('done', 'Done'), ],
                             default='draft', required=False, copy=False)
    payslips_count = fields.Integer(compute='_compute_payslips_count')


    @api.onchange('company_id', 'number_unit_id')
    def get_batch_ids(self):
        for rec in self:
            employees = self.env['hr.employee'].sudo().search(
                [('contract_id', '!=', False), ('contract_id.state', '=', 'open'), ('number_unit_id', '=',  self.number_unit_id.id),
                 ('company_id', '=', self.company_id.id)])
            rec.batch_ids = employees.ids

    def generate_batches(self):
        for rec in self:
            pay = []
            h = 0
            for line in rec.batch_ids:
                payslib = self.env['hr.payslip'].sudo().create({
                    'employee_id': line.id,
                    'date_from': rec.date_from,
                    'date_to': rec.date_to,
                    'contract_id': line.contract_id.id,
                    'struct_id': rec.struct_id.id,
                    'name': 'Salary Slip - ' + line.name,
                })
                payslib._onchange_employee()
                payslib._get_worked_day_lines()
                pay.append(payslib.id)
            rec.payslibs_ids = pay
            rec.state = "wait"

    def comput_sheet(self):
        for rec in self:
            for line in rec.payslibs_ids:
                line._onchange_employee()
                line._get_worked_day_lines()
                line.compute_sheet()
                line.action_payslip_done()
            rec.state = "done"

    def _compute_payslips_count(self):
        for payslip_run in self:
            payslip_run.payslips_count = len(payslip_run.payslibs_ids)

    def open_payslips(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "hr.payslip",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [['id', 'in', self.payslibs_ids.ids]],
            "name": "Payslips",
        }
