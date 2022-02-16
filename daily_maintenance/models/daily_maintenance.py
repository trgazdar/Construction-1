# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError
from odoo.tools import email_split, float_is_zero


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.request'

    date_after_maintenance = fields.Date(string='تاريخ التسليم بعد الصيانة', default=fields.Date.context_today, copy=False)
    maintenance_employee = fields.Many2one(
        'hr.employee',
        string='السائق المسلمة له')
    location_to = fields.Char(string='الموقع المرحلة علية')
    location_from = fields.Char(string='الموقع الواردة منه')
    employee = fields.Char('الموظف')



class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    maintenance_daily = fields.Integer('Maintenance After KW')
    code = fields.Char('كود')
    color = fields.Char('اللون')
    chasse_number = fields.Char('رقم الشاشية')
    brand = fields.Char('ماركة')
    made_in = fields.Char(' بلد المنشأ')
    year_made_in = fields.Char(' سنة الصنع')

    def _create_request(self, equipment):
        self.env['maintenance.request'].create({
            'name': _('Preventive Maintenance - %s', equipment.name),
            'request_date': fields.Date.today(),
            'schedule_date': fields.Date.today(),
            'category_id': equipment.category_id.id,
            'equipment_id': equipment.id,
            'maintenance_type': 'preventive',
            'owner_user_id': equipment.owner_user_id.id,
            'user_id': equipment.technician_user_id.id,
            'maintenance_team_id': equipment.maintenance_team_id.id or False,
            'duration': equipment.maintenance_duration,
            'company_id': equipment.company_id.id or self.env.company.id
            })


    def _generate_requests(self):
        """
            Generates maintenance request
        """
        equipments = self.env['maintenance.equipment'].sudo().search([])
        for equipment in equipments:
            if equipment.maintenance_daily and equipment.maintenance_daily > 0:
                equipment_work = self.env['daily.maintenance'].search([('equipment_id', '=', equipment.id),('request_done', '=', False)])
                total_work = sum(equipment_work.mapped('daily_work'))
                if total_work >= equipment.maintenance_daily:
                   equipment._create_request(equipment)
                   for line in equipment_work:
                        line.write({'request_done': True})



class DailyMaintenance(models.Model):
    _name = 'daily.maintenance'

    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment')
    category_id = fields.Many2one(
        'maintenance.equipment.category',
        string='Equipment Category',
        related='equipment_id.category_id')

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related='equipment_id.company_id')

    maintenance_team_id = fields.Many2one(
        'maintenance.team',
        string='Maintenance Team',
        related='equipment_id.maintenance_team_id')

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        related='equipment_id.employee_id')

    date = fields.Date(string='Date', default=fields.Date.context_today, copy=False)

    daily_work = fields.Integer('Daily Work')

    request_done = fields.Boolean('request done')












