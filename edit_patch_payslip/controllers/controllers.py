# -*- coding: utf-8 -*-
# from odoo import http


# class EditPatchPayslip(http.Controller):
#     @http.route('/edit_patch_payslip/edit_patch_payslip/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/edit_patch_payslip/edit_patch_payslip/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('edit_patch_payslip.listing', {
#             'root': '/edit_patch_payslip/edit_patch_payslip',
#             'objects': http.request.env['edit_patch_payslip.edit_patch_payslip'].search([]),
#         })

#     @http.route('/edit_patch_payslip/edit_patch_payslip/objects/<model("edit_patch_payslip.edit_patch_payslip"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('edit_patch_payslip.object', {
#             'object': obj
#         })
