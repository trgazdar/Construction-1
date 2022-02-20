# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Daily maintenance',
    'version': '14.1',
    'depends': ['mrp_maintenance','maintenance'],
    'sequence': 15,

    'data': [
        'security/ir.model.access.csv',
        'data/maintenance_cron.xml',
        'views/daily_maintenance.xml',

    ],

    'installable': True,

}
