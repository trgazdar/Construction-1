# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Analytic Report',
    'version': '14.1',
    'depends': ['account','analytic','stock','account_reports'],
    'sequence': 15,

    'data': [
        'security/ir.model.access.csv',
        'views/analytic_report_wizard.xml',
        'views/report.xml',

    ],

    'installable': True,

}
