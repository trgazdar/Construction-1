# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    def action_print_pdf_report(self):
        active_ids = self.env['stock.valuation.layer'].browse(self.env.context.get('active_ids'))
        data = {'data': active_ids.ids}
        return self.env.ref('inventory_valuation.print_report_id').report_action(self, data= data)


class ProjectReport(models.AbstractModel):
    _name = 'report.inventory_valuation.print_report'

    @api.model
    def _get_report_values(self, docids, data):
        lines = self.env['stock.valuation.layer'].search([('id', 'in', data['data'])])
        return {
            'lines': lines,
        }


