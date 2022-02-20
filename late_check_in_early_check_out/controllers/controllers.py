# -*- coding: utf-8 -*-
# from odoo import http


# class LateCheckInEarlyCheckOut(http.Controller):
#     @http.route('/late_check_in_early_check_out/late_check_in_early_check_out/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/late_check_in_early_check_out/late_check_in_early_check_out/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('late_check_in_early_check_out.listing', {
#             'root': '/late_check_in_early_check_out/late_check_in_early_check_out',
#             'objects': http.request.env['late_check_in_early_check_out.late_check_in_early_check_out'].search([]),
#         })

#     @http.route('/late_check_in_early_check_out/late_check_in_early_check_out/objects/<model("late_check_in_early_check_out.late_check_in_early_check_out"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('late_check_in_early_check_out.object', {
#             'object': obj
#         })
