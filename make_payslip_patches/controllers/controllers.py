# -*- coding: utf-8 -*-
# from odoo import http


# class MakePayslipPatches(http.Controller):
#     @http.route('/make_payslip_patches/make_payslip_patches/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/make_payslip_patches/make_payslip_patches/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('make_payslip_patches.listing', {
#             'root': '/make_payslip_patches/make_payslip_patches',
#             'objects': http.request.env['make_payslip_patches.make_payslip_patches'].search([]),
#         })

#     @http.route('/make_payslip_patches/make_payslip_patches/objects/<model("make_payslip_patches.make_payslip_patches"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('make_payslip_patches.object', {
#             'object': obj
#         })
