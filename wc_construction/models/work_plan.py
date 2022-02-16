# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class WorkPlanLines(models.Model):
    _name = 'work.plan.line'

    product_id = fields.Many2one(comodel_name="product.product",domain=[('is_tender_item','=',True)], string="tender Item", required=True, )
    work_plan_item_id = fields.Many2one(comodel_name="work.plan.items.line", string="Work Plan Item", required=False, )
    # category_id = fields.Many2one(comodel_name="work.plan.items.cat", string="category", required=False,related="work_plan_item_id.category_id" )
    quantity = fields.Float(string="Quantity",  required=False, )
    tender_quantity = fields.Float(string="Tender Quantity",  required=False, )
    outstanding = fields.Float(string="outstanding quantity",  required=False, )
    category_quantity = fields.Float(string="Category Quantity",  required=False, )
    work_plan_id = fields.Many2one(comodel_name="work.plan", string="", required=False, )
    work_plan_items_id = fields.Many2one(comodel_name="work.plan.items.cat", string="category", required=False, )
    plan_items_id = fields.Many2one(comodel_name="work.plan.items", string="Work Plan Item", required=False, )
    update_product = fields.Boolean(string="Update Products", )

    @api.constrains('work_plan_items_id')
    def create_work_plan_items_id(self):
        for rec in self:
            if rec.work_plan_items_id:
                rec.work_plan_id=self.env['work.plan'].search([('project_id','=',rec.work_plan_items_id.project_id.id)]).id


    @api.constrains('plan_items_id')
    def create_work_items_id(self):
        for rec in self:
            if rec.plan_items_id:
                rec.work_plan_id=self.env['work.plan'].search([('project_id','=',rec.plan_items_id.project_id.id)]).id



    @api.onchange('product_id')
    def get_product_data(self):
        for rec in self:
            for line in rec.work_plan_id.quotation_id.order_line:
                if rec.product_id.id == line.product_id.id:
                    # rec.price_unit = line.price_unit
                    rec.tender_quantity = line.product_uom_qty
                    # rec.product_uom_id = line.product_uom_id.id
            if rec.work_plan_items_id:
                rec.tender_quantity = rec.work_plan_items_id.project_id.project_tender_ids.filtered(
                    lambda
                        m: m.name == rec.product_id.name).tender_qty or rec.plan_items_id.project_id.project_tender_ids.filtered(
                    lambda m: m.name == rec.product_id.name).tender_qty
                cats=self.env['work.plan.items.cat'].search([('project_id','=',rec.work_plan_items_id.project_id.id),('create_uid','!=',False)])
                lines=False
                if cats:
                    lines=self.search([('work_plan_items_id','in',cats.ids),("product_id","=",rec.product_id.id)])
                if lines:
                    rec.outstanding=rec.tender_quantity-sum(list(lines.mapped('quantity')))
                else:
                    rec.outstanding=rec.tender_quantity
            if rec.plan_items_id:
                rec.category_quantity=sum(list(
                    rec.plan_items_id.category_id.work_plan_line_items_ids.filtered(
                        lambda m: m.product_id.id == rec.product_id.id).mapped('quantity')))
                rec.tender_quantity = rec.work_plan_items_id.project_id.project_tender_ids.filtered(
                    lambda
                        m: m.name == rec.product_id.name).tender_qty or rec.plan_items_id.project_id.project_tender_ids.filtered(
                    lambda m: m.name == rec.product_id.name).tender_qty

                items = self.env['work.plan.items'].search(
                    [('category_id', '=', rec.plan_items_id.category_id.id), ('create_uid', '!=', False)])
                lines = False
                if items:
                    lines = self.search(
                        [('plan_items_id', 'in', items.ids), ("product_id", "=", rec.product_id.id)])
                if lines:
                    rec.outstanding = rec.category_quantity - sum(list(lines.mapped('quantity')))
                else:
                    rec.outstanding = rec.category_quantity


    @api.onchange('update_product', 'quantity','product_id')
    def get_products_from_contract_quotation(self):
        for rec in self:
            products = []
            # for res in rec.work_plan_id.quotation_id.order_line:
            #     products.append(res.product_id.id)
            if rec.work_plan_items_id:
                for item in rec.work_plan_items_id.project_id.project_tender_ids:
                    # product = self.env['product.product'].sudo().search([('name', '=', item.name)])
                    products.append(item.related_product.id)
            if rec.plan_items_id:
                for item in rec.plan_items_id.category_id.work_plan_line_items_ids:
                    products.append(item.product_id.id)

            return {'domain': {'product_id': [('id', 'in', products)]}}

    @api.onchange('product_id','work_plan_item_id')
    def filter_work_plan_items(self):
        work_plan_items = self.env['work.plan.items'].search([('project_id','=',self.work_plan_id.project_id.id)])
        work_plan_items_line = []
        for rec in work_plan_items:
            for line in rec.work_plan_items_line_ids:
                work_plan_items_line.append(line.id)

        return {'domain':{'work_plan_item_id':[('id','in',work_plan_items_line)]}}


class WorkPlan(models.Model):
    _name = 'work.plan'

    contract_id = fields.Many2one(comodel_name="owner.contract",domain=[('type','=','subcontractor')] ,string="Contract", required=False, )

    quotation_id = fields.Many2one(comodel_name="sale.order", string="Quotation",compute='get_customer',store=True, required=False, )
    project_id = fields.Many2one(comodel_name="project.project", string="Project", required=True, )
    customer_id = fields.Many2one(comodel_name="res.partner", string="Vendor",compute='get_customer',store=True, required=False, )
    date = fields.Date(string="Date", required=False, default=fields.Date.context_today)
    work_plan_line_ids = fields.One2many(comodel_name="work.plan.line", inverse_name="work_plan_id", string="", required=False, )

    @api.depends('project_id')
    def get_customer(self):
        if self.project_id:
            self.quotation_id = self.project_id.so_id.id
            self.customer_id = self.project_id.partner_id.id
        else:
            self.quotation_id = False
            self.customer_id = False

    @api.onchange('work_plan_line_ids')
    def action_restriction_plan_line(self):
        for i in self.work_plan_line_ids:
            total_qty = i.quantity
            tender_quantity = i.tender_quantity
            for j in self.work_plan_line_ids:
                if i.id == j.id:
                    continue
                if i.product_id.id == j.product_id.id and i.work_plan_item_id.id == j.work_plan_item_id.id:
                    total_qty = total_qty + j.quantity
                if total_qty > tender_quantity:
                    raise ValidationError("There Is No Available Quantity")

    @api.onchange('contract_id')
    def get_contract_data(self):
        # lines = []
        self.project_id = self.contract_id.project_id.id
        # self.customer_id = self.contract_id.customer_id.id

        # for rec in self.contract_id.contract_line_ids:
        #     lines.append((0, 0, {
        #         'product_id': rec.product_id.id,
        #         'account_id': self._get_computed_account_to_lines(rec.product_id),
        #         'name': rec.product_id.name,
        #         'price_unit': rec.price_unit,
        #         'total_contract_qty': rec.quantity,
        #         'quantity': 0,
        #         'product_uom_id': rec.product_uom_id.id,
        #         'exclude_from_invoice_tab': False,
        #         'tax_ids': rec.tax_id.ids,
        #     }))
        # self._onchange_partner_id()
        # self.invoice_line_ids = lines
        #
        # for line in self.invoice_line_ids:
        #     line._onchange_price_subtotal()
        # self._onchange_invoice_line_ids()






