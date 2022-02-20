# -*- coding: utf-8 -*-


from odoo import models, fields, api
from datetime import datetime as dt, date
from time import time
import datetime


class HrAttendanceInherit(models.Model):
    _inherit = 'hr.attendance'

    late = fields.Float(string='Late', compute='compute_early_late', )
    over_time = fields.Float(string='Overtime', readonly=True)
    early_leave = fields.Float(string='Early Leave', readonly=True)
    early_sign_in = fields.Float(string='Early Sign In', readonly=True)
    hour_from = fields.Float(string="Hour From", compute="get_shift")
    hour_to = fields.Float(string="Hour To", compute="get_shift")
    penalties_1 = fields.Float(string="Penalties 1", readonly=True)
    penalties_2 = fields.Float(string="Penalties 2", readonly=True)
    hr_attend = fields.Many2one(comodel_name="hr.payslip", string="", required=False, )
    worked_hours = fields.Float(string='Worked Hours', readonly=True)

    @api.depends('employee_id')
    def get_shift(self):
        for rec in self:
            if rec.check_in and rec.check_out:
                shift = self.env['employee.shift.line'].search(
                    [('shift_name_id', '=', rec.employee_id.id), ], limit=1)
                rec.hour_from = shift.hour_from
                rec.hour_to = shift.hour_to
                rec.worked_hours = shift.hour_to - shift.hour_from
            else:
                rec.hour_from = rec.hour_from
                rec.hour_to = rec.hour_to
                rec.worked_hours = rec.worked_hours

    @api.depends('check_in', 'check_out', 'hour_from', 'hour_to')
    def compute_early_late(self):
        for rec in self:
            rec.late = False
            penalties = self.env['hr.contract'].sudo().search([('employee_id', '=', rec.employee_id.id)], limit=1)
            if rec.check_in:
                check_in_hour = rec.check_in.hour + (rec.check_in.minute / 60) + 2
                late_in = check_in_hour - rec.hour_from
                if late_in >= 0:
                    rec.late = late_in
                    rec.early_sign_in = 0
                else:
                    rec.early_sign_in = -late_in
                    rec.late = 0
                if 1 >= late_in > 0:
                    rec.penalties_1 = penalties.penalties_1
                    rec.penalties_2 = 0
                elif late_in > 1:
                    rec.penalties_2 = penalties.penalties_2
                    rec.penalties_1 = penalties.penalties_1
                else:
                    rec.penalties_2 = 0
                    rec.penalties_1 = 0
            if rec.check_out:
                check_out_hour = rec.check_out.hour + (rec.check_out.minute / 60) + 2
                late_out = rec.hour_to - check_out_hour
                if late_out >= 0:
                    rec.over_time = 0
                    rec.early_leave = late_out
                else:
                    rec.early_leave = 0
                    rec.over_time = -late_out

    def check_attendance(self):
        attendance = self.env['hr.attendance'].sudo().search([])
        for x in attendance:
            x.sudo().compute_early_late()


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    shift_name_ids = fields.One2many(comodel_name="employee.shift.line", inverse_name="shift_name_id",
                                     string="", required=False, )


class HrContractInherit(models.Model):
    _inherit = 'hr.contract'

    penalties_1 = fields.Float(string="Penalties 1")
    penalties_2 = fields.Float(string="Penalties 2")


class EmployeeShiftLine(models.Model):
    _name = 'employee.shift.line'

    name = fields.Char(string="", required=False, )
    shift_name_id = fields.Many2one('hr.employee', string="")
    shift_payroll_id = fields.Many2one('hr.payslip', string="")
    hour_from = fields.Float(string="Hour From")
    hour_to = fields.Float(string="Hour To")


class EditHrPayslip(models.Model):
    _inherit = 'hr.payslip'

    hr_attend_ids = fields.One2many(comodel_name="hr.attendance", inverse_name="hr_attend", string="",
                                    required=False, compute="get_hr_attend_ids")
    shift_name_ids = fields.One2many(comodel_name="employee.shift.line", inverse_name="shift_payroll_id",
                                     string="", required=False, compute="get_shift_name_ids")
    overtime_payroll_ids = fields.One2many(comodel_name="hr.overtime", inverse_name="overtime_payroll_id", string="",
                                           required=False, compute="get_overtime_payroll_ids")
    number_of_days_to_attend = fields.Integer(string="Number of days to attend", readonly=True, )
    total_penalties_1 = fields.Float(string="Total Penalties1", readonly=True, )
    total_penalties_2 = fields.Float(string="Total Penalties2", readonly=True, )
    sum_penalties = fields.Float(string="Sum Penalties", readonly=True, )

    @api.depends('employee_id', 'date_from', 'date_to', )
    def get_hr_attend_ids(self):
        self.hr_attend_ids = False
        attend = self.env['hr.attendance'].search([
            ('employee_id', '=', self.employee_id.id),
            ('check_in', '<=', self.date_to),
            ('check_in', '>=', self.date_from),
        ])
        if attend:
            self.hr_attend_ids = attend
        else:
            self.hr_attend_ids = False
        self.number_of_days_to_attend = len(attend)
        self.total_penalties_1 = sum(list(attend.mapped('penalties_1')))
        self.total_penalties_2 = sum(list(attend.mapped('penalties_2')))
        self.sum_penalties = self.total_penalties_1 + self.total_penalties_2

    @api.depends('employee_id', 'date_from', 'date_to', )
    def get_shift_name_ids(self):
        self.shift_name_ids = False
        shift_attend = self.env['hr.employee'].search([
            ('id', '=', self.employee_id.id),
            ('shift_name_ids', '!=', False),
        ])
        if shift_attend:
            self.shift_name_ids = shift_attend.shift_name_ids
        else:
            self.shift_name_ids = False

    @api.depends('employee_id', 'date_from', 'date_to', )
    def get_overtime_payroll_ids(self):
        self.overtime_payroll_ids = False
        overtime = self.env['hr.overtime'].search([
            ('employee_id', '=', self.employee_id.id),
            ('date_to', '<=', self.date_to),
            ('date_from', '>=', self.date_from),
            ('state', '=', 'approved'),
        ])
        if overtime:
            self.overtime_payroll_ids = overtime
        else:
            self.overtime_payroll_ids = False
