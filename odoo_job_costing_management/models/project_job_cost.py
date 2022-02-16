# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectProject(models.Model):
    _inherit = 'project.project'

    type_of_construction = fields.Selection(
        [('agricultural', 'Agricultural'),
         ('residential', 'Residential'),
         ('commercial', 'Commercial'),
         ('institutional', 'Institutional'),
         ('industrial', 'Industrial'),
         ('heavy_civil', 'Heavy civil'),
         ('environmental', 'Environmental'),
         ('other', 'other')],
        string='Types of Construction'
    )
    location_id = fields.Char(string='Location', required=True, default='')
    notes_ids = fields.One2many(
        'note.note',
        'project_id',
        string='Notes',
    )
    notes_count = fields.Integer(
        compute='_compute_notes_count',
        string="Notes")

    @api.depends('notes_ids')
    def _compute_notes_count(self):
        for project in self:
            project.notes_count = len(project.notes_ids)

    @api.depends('notes_ids')
    def view_notes(self):
        for rec in self:
            res = self.env.ref('odoo_job_costing_management.action_project_note_note')
            res = res.read()[0]
            res['domain'] = str([('project_id', 'in', rec.ids)])
        return res
