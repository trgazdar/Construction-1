# -*- coding: utf-8 -*-

from collections import defaultdict
from datetime import datetime, date, time
import pytz

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrPayslipEmployeesInherit(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    def _check_undefined_slots(self, work_entries, payslip_run):
        """
        Check if a time slot in the contract's calendar is not covered by a work entry
        """
        work_entries_by_contract = defaultdict(lambda: self.env['hr.work.entry'])
        for work_entry in work_entries:
            work_entries_by_contract[work_entry.contract_id] |= work_entry

        for contract, work_entries in work_entries_by_contract.items():
            calendar_start = pytz.utc.localize(
                datetime.combine(max(contract.date_start, payslip_run.date_start), time.min))
            calendar_end = pytz.utc.localize(
                datetime.combine(min(contract.date_end or date.max, payslip_run.date_end), time.max))
            outside = contract.resource_calendar_id._attendance_intervals_batch(calendar_start, calendar_end)[
                          False] - work_entries._to_intervals()
            if outside == 1:
                raise UserError(
                    _("Some part of %s's calendar is not covered by any work entry. Please complete the schedule.",
                      contract.employee_id.name))

    def _get_employees(self):
        # YTI check dates too
        domane = self._get_available_contracts_domain()
        if self.env.context['active_model'] =='hr.payslip.run':
            rec=self.env[self.env.context['active_model']].sudo().search([('id','=',self.env.context['active_id'])])
            domane.append(('number_unit_id','=',rec.number_unit_id.id))
        return self.env['hr.employee'].search(domane)


class HrPayslipRunInherit(models.Model):
    _inherit = 'hr.payslip.run'

    number_unit_id = fields.Many2one(comodel_name="number.unit", string="Number Unit", required=False, )


class NumberUnit(models.Model):
    _name = 'number.unit'
    _description = 'Number Unit'

    name = fields.Char(string="Name", )
    id = fields.Integer(string="ID", required=False, )


class EditHrEmployee(models.Model):
    _inherit = 'hr.employee'

    number_unit_id = fields.Many2one(comodel_name="number.unit", string="Number Unit", required=False, )
