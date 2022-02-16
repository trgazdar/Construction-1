# -*- coding: utf-8 -*-

from odoo import fields, models, api


class Project(models.Model):
    _inherit = "project.project"

    def show_inspection(self):
        self.ensure_one()
        res = self.env.ref('odoo_project_phases.action_phase_type')
        res = res.read()[0]
        res['domain'] = str([('project_id', '=', self.id)])
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
