# -*- coding: utf-8 -*-

from odoo import models, fields, api


class NetSalary(models.TransientModel):
    _name = 'net.salary'
    _description = 'Net Salary'

    date_from = fields.Date(string="From", required=True, )
    date_to = fields.Date(string="To", required=True, )
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.company)
    employee_ids = fields.Many2many('hr.employee', string="Employee", required=False, )
    number_unit_ids = fields.Many2many(comodel_name="number.unit", string="Number Unit", required=False, )

    def get_net_salary(self):
        for rec in self:
            number_unit_list = []
            date_wizzerd = {}
            date_wizzerd['company'] = rec.company_id.name
            date_wizzerd['date_from'] = rec.date_from
            date_wizzerd['date_to'] = rec.date_to
            data = {}
            lest = []
            if not rec.employee_ids:
                rec.employee_ids = self.env['hr.employee'].sudo().search(
                    [('company_id', '=', rec.company_id.id), ('number_unit_id', '=', rec.number_unit_ids.id)]).ids
            if not rec.number_unit_ids:
                rec.number_unit_ids = self.env['number.unit'].sudo().search([]).ids
            for number_unit in rec.number_unit_ids:
                number_unit_list.append(number_unit.name)
            payslips = self.env['hr.payslip'].sudo().search(
                [('employee_id', 'in', rec.employee_ids.ids),
                 ('date_from', '>=', rec.date_from),
                 ('date_to', '<=', rec.date_to)])
            work_day_total = 0
            total_basic_salary = 0
            badl_sakn = 0
            entqalat = 0
            edafe = 0
            etselat = 0
            tabeat_aml = 0
            foot = 0
            other = 0
            moqatah = 0
            total_mosthaqat = 0
            loans = 0
            penalates = 0
            tamenat = 0
            arda = 0
            permeashin = 0
            total = 0
            net_total = 0
            for payslip in payslips:
                dec = {'employee': payslip.employee_id.name, 'code_employee': payslip.employee_id.pin,
                       'jop': payslip.employee_id.job_title, 'work_day': payslip.number_of_days + 1,
                       '????????????_??????????????': 0, '??????_??????': 0, '????????????????': 0, '??????????': 0, '??????????????': 0, '??????????_??????': 0,
                       '????????': 0, '????????': 0, '????????????': 0, '????????????_??????????????????': 0, '??????': 0, '????????????': 0, '??????????????': 0,
                       '??????????_??????????': 0, '??????????_????????_??????': 0, '????????????????': 0, '????????_??????????????': 0}
                work_day_total += payslip.number_of_days + 1
                for salary in payslip.line_ids:
                    if salary.salary_rule_id.id == self.env.ref('__export__.hr_salary_rule_275_40baede9').id:
                        dec['????????????_??????????????'] = salary.total
                        total_basic_salary += salary.total
                    elif salary.salary_rule_id.id == self.env.ref('__export__.hr_salary_rule_277_7055a60f').id:
                        dec['??????_??????'] = salary.total
                        badl_sakn += salary.total
                    elif salary.salary_rule_id.id == self.env.ref('__export__.hr_salary_rule_278_c956e8c3').id:
                        dec['????????????????'] = salary.total
                        entqalat += salary.total
                    elif salary.salary_rule_id.id == self.env.ref('__export__.hr_salary_rule_283_beb8fb2b').id:
                        dec['??????????'] = salary.total
                        edafe += salary.total
                    elif salary.salary_rule_id.id == self.env.ref('__export__.hr_salary_rule_280_3d932fcc').id:
                        dec['??????????????'] = salary.total
                        etselat += salary.total
                    elif salary.salary_rule_id.id == self.env.ref('__export__.hr_salary_rule_281_0860f6c0').id:
                        dec['??????????_??????'] = salary.total
                        tabeat_aml += salary.total
                    elif salary.salary_rule_id.id == self.env.ref('__export__.hr_salary_rule_279_158735c8').id:
                        dec['????????'] = salary.total
                        foot += salary.total
                    elif salary.salary_rule_id.id == self.env.ref('__export__.hr_salary_rule_282_7577b410').id:
                        dec['????????'] = salary.total
                        other += salary.total
                    elif salary.salary_rule_id.id == self.env.ref('__export__.hr_salary_rule_276_cff8bf45').id:
                        dec['????????????'] = salary.total
                        moqatah += salary.total
                    elif salary.salary_rule_id.id == self.env.ref('__export__.hr_salary_rule_284_a6ad207e').id:
                        dec['????????????_??????????????????'] = salary.total
                        total_mosthaqat += salary.total
                    elif salary.salary_rule_id.id == self.env.ref('__export__.hr_salary_rule_285_f6b7934a').id:
                        dec['??????'] = salary.total
                        loans += salary.total
                    elif salary.salary_rule_id.id == self.env.ref('__export__.hr_salary_rule_287_f23e1f09').id:
                        dec['????????????'] = salary.total
                        penalates += salary.total
                    elif salary.salary_rule_id.id == self.env.ref('__export__.hr_salary_rule_286_d2ed7b88').id:
                        dec['??????????????'] = salary.total
                        tamenat += salary.total
                    elif salary.salary_rule_id.id == self.env.ref('__export__.hr_salary_rule_289_69d9ad77').id:
                        dec['??????????_??????????'] = salary.total
                        arda += salary.total
                    elif salary.salary_rule_id.id == self.env.ref('__export__.hr_salary_rule_293_ea2d5f7f').id:
                        dec['??????????_????????_??????'] = salary.total
                        permeashin += salary.total
                    elif salary.salary_rule_id.id == self.env.ref('__export__.hr_salary_rule_290_a1c57636').id:
                        dec['????????????????'] = salary.total
                        total += salary.total
                    elif salary.salary_rule_id.id == self.env.ref('__export__.hr_salary_rule_294_a24d9a1c').id:
                        dec['????????_??????????????'] = salary.total
                        net_total += salary.total
                lest.append(dec)
            total_dec = {'employee': "",
                         'code_employee': "",
                         'jop': "????????????????",
                         'work_day': work_day_total,
                         '????????????_??????????????': total_basic_salary,
                         '??????_??????': badl_sakn,
                         '????????????????': entqalat,
                         '??????????': edafe,
                         '??????????????': etselat,
                         '??????????_??????': tabeat_aml,
                         '????????': foot,
                         '????????': other,
                         '????????????': moqatah,
                         '????????????_??????????????????': total_mosthaqat,
                         '??????': loans,
                         '????????????': penalates,
                         '??????????????': tamenat,
                         '??????????_??????????': arda,
                         '??????????_????????_??????': permeashin,
                         '????????????????': total,
                         '????????_??????????????': net_total,
                         }
            lest.append(total_dec)
            data['data'] = lest
            data['date_wizzerd'] = date_wizzerd
            data['number_unit_list'] = number_unit_list
            return self.env.ref('print_net_salary_employee.id_net_salary_report').report_action(self, data)
