# -*- coding: utf-8 -*-

from datetime import date

from odoo import models, fields, api, _
from odoo.exceptions import Warning

class ResPartner(models.Model):
    _inherit = "res.partner"

    job_id = fields.Many2one('job.costing')

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    job_cost_id_employee = fields.Many2one('job.costing')


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    job_id = fields.Many2one('job.costing')


class JobCosting(models.Model):
    _name = 'job.costing'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']  # odoo11
    #    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Job Costing"
    _rec_name = 'number'

    @api.model
    def create(self, vals):
        number = self.env['ir.sequence'].next_by_code('job.costing')
        vals.update({
            'number': number,
        })
        return super(JobCosting, self).create(vals)

    def unlink(self):
        for rec in self:
            if rec.state not in ('draft', 'cancel'):
                raise Warning(_('You can not delete Job Cost Sheet which is not draft or cancelled.'))
        return super(JobCosting, self).unlink()

    @api.depends(
        'job_cost_line_ids',
        'job_cost_line_ids.product_qty',
        'job_cost_line_ids.cost_price',
    )
    def _compute_material_total(self):
        for rec in self:
            rec.material_total = sum([(p.product_qty * p.cost_price) for p in rec.job_cost_line_ids])

    @api.depends(
        'subcontractor_line_ids',
        'subcontractor_line_ids.product_qty',
        'subcontractor_line_ids.cost_price',
    )
    def _compute_subcontractor_total(self):
        for rec in self:
            rec.subcontractor_total = sum([(p.product_qty * p.cost_price) for p in rec.subcontractor_line_ids])

    @api.depends(
        'job_labour_line_ids',
        'job_labour_line_ids.hours',
        'job_labour_line_ids.cost_price'
    )
    def _compute_labor_total(self):
        for rec in self:
            rec.labor_total = sum([(p.hours * p.cost_price) for p in rec.job_labour_line_ids])

    @api.depends(
        'equipment_line_ids',
        'equipment_line_ids.hours',
        'equipment_line_ids.cost_price'
    )
    def _compute_equipment_total(self):
        for rec in self:
            rec.equipment_total = sum([(p.hours * p.cost_price) for p in rec.equipment_line_ids])

    @api.depends(
        'job_overhead_line_ids',
        'job_overhead_line_ids.product_qty',
        'job_overhead_line_ids.cost_price'
    )
    def _compute_overhead_total(self):
        for rec in self:
            rec.overhead_total = sum([(p.product_qty * p.cost_price) for p in rec.job_overhead_line_ids])

    @api.depends(
        'other_line_ids',
        'other_line_ids.product_qty',
        'other_line_ids.cost_price'
    )
    def _compute_other_total(self):
        for rec in self:
            rec.other_total = sum([(p.product_qty * p.cost_price) for p in rec.other_line_ids])

    @api.depends(
        'material_total',
        'labor_total',
        'overhead_total',
        'subcontractor_total',
        'equipment_total',
        'other_total'
    )
    def _compute_jobcost_total(self):
        for rec in self:
            rec.jobcost_total = rec.material_total + rec.labor_total + rec.overhead_total + rec.subcontractor_total + rec.equipment_total + rec.other_total

    def _purchase_order_line_count(self):
        purchase_order_lines_obj = self.env['purchase.order.line']
        for order_line in self:
            order_line.purchase_order_line_count = purchase_order_lines_obj.search_count(
                [('job_cost_id', '=', order_line.id)])

    def _timesheet_line_count(self):
        hr_timesheet_obj = self.env['account.analytic.line']
        for timesheet_line in self:
            timesheet_line.timesheet_line_count = hr_timesheet_obj.search_count(
                [('job_cost_id', '=', timesheet_line.id)])

    def _account_invoice_line_count(self):
        account_invoice_lines_obj = self.env['account.move.line']
        for invoice_line in self:
            invoice_line.account_invoice_line_count = account_invoice_lines_obj.search_count(
                [('job_cost_id', '=', invoice_line.id)])

    @api.onchange('project_id')
    def _onchange_project_id(self):
        for rec in self:
            rec.analytic_id = rec.project_id.analytic_account_id.id

    number = fields.Char(readonly=True, default='New', copy=False, )
    name = fields.Char(required=True, copy=True, default='New', string='Name', )
    notes_job = fields.Text(required=False, copy=True, string='Job Cost Details')
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user, string='Created By', readonly=True)
    description = fields.Char(string='Description', )
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.user.company_id.currency_id, readonly=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id, string='Company',
                                 readonly=True)
    project_id = fields.Many2one('project.project', string='Project', )
    analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account', )
    contract_date = fields.Date(string='Contract Date', )
    start_date = fields.Date(string='Create Date', readonly=True, default=fields.Date.today(), )
    complete_date = fields.Date(string='Closed Date', readonly=True, )
    material_total = fields.Float(string='Total Material Cost', compute='_compute_material_total', store=True,digits='Payment Decimal' )
    subcontractor_total = fields.Float(string='Total SubContractor', compute='_compute_subcontractor_total',
                                       store=True,digits='Payment Decimal' )
    equipment_total = fields.Float(string='Total Equipment', compute='_compute_equipment_total', store=True, digits='Payment Decimal')
    other_total = fields.Float(string='Total Other', compute='_compute_other_total', store=True, digits='Payment Decimal')
    labor_total = fields.Float(string='Total Labour Cost', compute='_compute_labor_total', store=True, digits='Payment Decimal')
    overhead_total = fields.Float(string='Total Overhead Cost', compute='_compute_overhead_total', store=True,digits='Payment Decimal' )
    jobcost_total = fields.Float(string='Breakdown Cost', compute='_compute_jobcost_total', store=True,digits='Payment Decimal' )

    job_cost_line_ids = fields.One2many('job.cost.line', 'direct_id', string='Direct Materials', copy=False,
                                        domain=[('job_type', '=', 'material')], )
    job_labour_line_ids = fields.One2many('job.cost.line', 'direct_id', string='Direct Materials', copy=False,
                                        domain=[('job_type', '=', 'labour')], )
    # job_labour_line_ids = fields.One2many('hr.employee', 'job_cost_id_employee', string='Labours', copy=False,)

    job_overhead_line_ids = fields.One2many('job.cost.line', 'direct_id', string='Direct Materials', copy=False,
                                            domain=[('job_type', '=', 'overhead')], )

    # subcontractor_line_ids = fields.One2many('res.partner', 'job_id', string='Subcontractors', copy=False,)
    subcontractor_line_ids = fields.One2many('job.cost.line', 'direct_id', string='Direct Materials', copy=False,
                                        domain=[('job_type', '=', 'subcontractor')], )
    # equipment_line_ids = fields.One2many('maintenance.equipment', 'job_id', string='Direct Materials', copy=False,)
    equipment_line_ids = fields.One2many('job.cost.line', 'direct_id', string='Direct Materials', copy=False,
                                        domain=[('job_type', '=', 'equipment')], )

    other_line_ids = fields.One2many('job.cost.line', 'direct_id', string='Direct Materials', copy=False,
                                     domain=[('job_type', '=', 'other')], )

    partner_id = fields.Many2one('res.partner', string='Customer', required=True, related='project_id.partner_id')
    state = fields.Selection(
        selection=[('draft', 'Draft'), ('confirm', 'Confirmed'), ('approve', 'Approved'), ('done', 'Done'),
                   ('cancel', 'Canceled'), ], string='State', ttracking=True, default=lambda self: _('draft'), )
    task_id = fields.Many2one('project.task', string='Job Order', related='tender_id.related_task_id')
    so_number = fields.Char(string='Sale Reference')
    purchase_order_line_count = fields.Integer(compute='_purchase_order_line_count')
    purchase_order_line_ids = fields.One2many("purchase.order.line", 'job_cost_id', )
    timesheet_line_count = fields.Integer(compute='_timesheet_line_count')
    timesheet_line_ids = fields.One2many('account.analytic.line', 'job_cost_id', )
    account_invoice_line_count = fields.Integer(compute='_account_invoice_line_count')
    account_invoice_line_ids = fields.One2many("account.move.line", 'job_cost_id', )
    tender_id = fields.Many2one('project.tender', string='Tender', )
    tender_qty = fields.Float(string='Tender Qty', related='tender_id.tender_qty')

    def action_draft(self):
        for rec in self:
            rec.write({
                'state': 'draft',
            })

    def action_confirm(self):
        for rec in self:
            rec.write({
                'state': 'confirm',
            })

    def action_approve(self):
        for rec in self:
            rec.write({
                'state': 'approve',
            })

    def action_done(self):
        for rec in self:
            rec.write({
                'state': 'done',
                'complete_date': date.today(),
            })

    def action_cancel(self):
        for rec in self:
            rec.write({
                'state': 'cancel',
            })

    def action_view_purchase_order_line(self):
        self.ensure_one()
        purchase_order_lines_obj = self.env['purchase.order.line']
        cost_ids = purchase_order_lines_obj.search([('job_cost_id', '=', self.id)]).ids
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Order Line',
            'res_model': 'purchase.order.line',
            'res_id': self.id,
            'domain': "[('id','in',[" + ','.join(map(str, cost_ids)) + "])]",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'target': self.id,
        }
        return action

    def action_view_hr_timesheet_line(self):
        hr_timesheet = self.env['account.analytic.line']
        cost_ids = hr_timesheet.search([('job_cost_id', '=', self.id)]).ids
        action = self.env.ref('hr_timesheet.act_hr_timesheet_line').read()[0]
        action['domain'] = [('id', 'in', cost_ids)]
        return action

    def action_view_vendor_bill_line(self):
        account_invoice_lines_obj = self.env['account.move.line']
        cost_ids = account_invoice_lines_obj.search([('job_cost_id', '=', self.id)]).ids
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Account Invoice Line',
            'res_model': 'account.move.line',
            'res_id': self.id,
            'domain': "[('id','in',[" + ','.join(map(str, cost_ids)) + "])]",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'target': self.id,
        }
        action['context'] = {
            'create': False,
            'edit': False,
        }
        return action
