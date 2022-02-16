# -*- coding: utf-8 -*-

from odoo import models, fields

class AccountInvoiceLine(models.Model):
    _inherit = 'account.move.line'
    
    job_cost_id = fields.Many2one(comodel_name="job.costing",string='Job Cost Center',store=True)
    job_cost_line_id = fields.Many2one(comodel_name="job.cost.line",string='Job Cost Line',store=True)
    

# class AccountInvoice(models.Model):
#     _inherit = 'account.move'
#
#     def _prepare_invoice_line_from_po_line(self, line):
#         data = super(
#             AccountInvoice, self
#         )._prepare_invoice_line_from_po_line(line)
#         data.update({
#             'job_cost_id': line.job_cost_id.id,
#             'job_cost_line_id': line.job_cost_line_id.id,
#         })
#         return data
