# -*- coding: utf-8 -*-
# from odoo import http


# class LoansAndAddvance(http.Controller):
#     @http.route('/loans_and_addvance/loans_and_addvance/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/loans_and_addvance/loans_and_addvance/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('loans_and_addvance.listing', {
#             'root': '/loans_and_addvance/loans_and_addvance',
#             'objects': http.request.env['loans_and_addvance.loans_and_addvance'].search([]),
#         })

#     @http.route('/loans_and_addvance/loans_and_addvance/objects/<model("loans_and_addvance.loans_and_addvance"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('loans_and_addvance.object', {
#             'object': obj
#         })
