# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, _


class AnalyticAccountReport(models.TransientModel):
    _name = 'analytic.report.wizard'
    _description = 'Analytic Account Report'

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account',)
    from_date = fields.Date('Date From')
    to_date = fields.Date('Date To')
    product_id = fields.Many2many('product.product', string='Product')
    location_from = fields.Many2one(
        'stock.location', 'Location From ')
    location_to = fields.Many2one(
        'stock.location', 'Location to')


    def print_report(self):
        data = {'analytic_account_id': self.analytic_account_id.id,
                'from_date': self.from_date,
                'to_date': self.to_date,
                'product_id' : self.product_id.ids,
                'location_from': self.location_from.id,
                'location_to': self.location_to.id}
        return self.env.ref('janobi_analytic_report.print_report_analytic_account').report_action(self, data=data)




class AnalyticAccountReport(models.AbstractModel):
    _name = 'report.janobi_analytic_report.analytic_report'


    @api.model
    def _get_report_values(self, docids, data):
        total_amount = 0
        total_done_qty= 0
        total_amount_product = 0
        qty_done = 0
        lines = []
        analytic = self.env['account.analytic.account'].browse(data['analytic_account_id'])
        analytic_account = self.env['account.analytic.line'].search([('account_id','=',data['analytic_account_id']),('date','>=',data['from_date']),('date','<=',data['to_date'])])
        if analytic_account:
            total_amount = sum(analytic_account.mapped('amount'))
        stock_lines = self.env['stock.move.line'].search([('product_id','in',data['product_id']),('date','>=',data['from_date']),('date','<=',data['to_date']),
                                                          ('location_id','=',data['location_from']),('location_dest_id','=',data['location_to'])])
        if stock_lines:
            total_done_qty = sum(stock_lines.mapped('qty_done'))
        for pro in data['product_id']:
            product_name = self.env['product.product'].browse(pro).name
            product = self.env['stock.move.line'].search(
                [('product_id', '=', pro), ('date', '>=', data['from_date']),
                 ('date', '<=', data['to_date']),
                 ('location_id', '=', data['location_from']), ('location_dest_id', '=', data['location_to'])])
            if product:
                qty_done = sum(product.mapped('qty_done'))

                total_amount_product = qty_done * (total_amount/total_done_qty)

            vals = {
                    'product_name': product_name,
                    'total_amount_product': round(total_amount_product, 2),
                    'qty_done': qty_done
             }
            lines.append(vals)
        return {

                'lines' : lines,
                 'analytic' : analytic,
                 'total_amount' : total_amount,

            }












