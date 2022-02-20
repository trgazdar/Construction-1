# -*- coding: utf-8 -*-
# from odoo import http


# class PrintNetSalaryEmployee(http.Controller):
#     @http.route('/print_net_salary_employee/print_net_salary_employee/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/print_net_salary_employee/print_net_salary_employee/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('print_net_salary_employee.listing', {
#             'root': '/print_net_salary_employee/print_net_salary_employee',
#             'objects': http.request.env['print_net_salary_employee.print_net_salary_employee'].search([]),
#         })

#     @http.route('/print_net_salary_employee/print_net_salary_employee/objects/<model("print_net_salary_employee.print_net_salary_employee"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('print_net_salary_employee.object', {
#             'object': obj
#         })
