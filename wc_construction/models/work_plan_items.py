# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class WorkPlanItemsLines(models.Model):
    _name = 'work.plan.items.line'

    name = fields.Char(string="Name", required=True, )
    work_plan_items_id = fields.Many2one(comodel_name="work.plan.items", string="", required=False, )
    category_id = fields.Many2one(comodel_name="work.plan.items.cat", string="category", required=False, )


class WorkPlanItems(models.Model):
    _name = 'work.plan.items'

    name = fields.Char(string="", required=True, )
    project_id = fields.Many2one(comodel_name="project.project", string="Project", required=True, )
    category_id = fields.Many2one(comodel_name="work.plan.items.cat", string="category", required=True, )
    work_plan_line_ids = fields.One2many(comodel_name="work.plan.line", inverse_name="plan_items_id", string="",
                                         required=False, )

    work_plan_items_line_ids = fields.One2many(comodel_name="work.plan.items.line", inverse_name="work_plan_items_id",
                                               string="", required=False, )

    @api.constrains('work_plan_line_ids')
    def check_total_quantity(self):
        for rec in self:
            for item in rec.category_id.work_plan_line_items_ids:
                if sum(list(rec.work_plan_line_ids.filtered(
                        lambda m: m.product_id.id == item.product_id.id).mapped('quantity'))) > sum(list(
                    rec.category_id.work_plan_line_items_ids.filtered(
                        lambda m: m.product_id.id == item.product_id.id).mapped('quantity'))):
                    raise UserError(_("Item %s maximum is %s" % (item.product_id.name, sum(list(
                        rec.category_id.work_plan_line_items_ids.filtered(
                            lambda m: m.product_id.id == item.product_id.id).mapped('quantity'))))))


class work_plan_items_cat(models.Model):
    _name = 'work.plan.items.cat'
    _rec_name = 'all_name'
    _description = 'New Description'

    name = fields.Char(required=True)
    parent_id = fields.Many2one(comodel_name="work.plan.items.cat", string="", required=False, )
    project_id = fields.Many2one(comodel_name='project.project', string='Project Name')
    work_plan_line_items_ids = fields.One2many(comodel_name="work.plan.line", inverse_name="work_plan_items_id",
                                               string="", required=False, )
    all_name = fields.Char(string="", required=False, compute="get_all_name", store=True)

    def go_work_plan_items(self):
        return {
            'name': _('Work Plan Items Cat'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'work.plan.items',
            'context': {'default_project_id': self.project_id.id, 'default_category_id': self.id},
            # 'target': 'new',
        }

    @api.constrains('work_plan_line_items_ids')
    def check_total_quantity(self):
        for rec in self:
            for item in rec.project_id.project_tender_ids:
                total_quantity = sum(list(rec.work_plan_line_items_ids.filtered(
                    lambda m: m.product_id.name == item.name).mapped('quantity')))
                if total_quantity > item.tender_qty:
                    raise UserError(_("Item %s maximum is %s" % (item.name, item.tender_qty)))

    @api.depends("name", "parent_id")
    @api.constrains("name", "parent_id")
    def get_all_name(self):
        for rec in self:
            rec.all_name = rec.name
            if rec.parent_id:
                rec.all_name += " / " + rec.parent_id.all_name
