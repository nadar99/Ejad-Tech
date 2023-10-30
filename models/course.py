# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions


class Course(models.Model):
    _name = 'openacademy.course'
    _description = 'Open Academy Courses'

    name = fields.Char(string="Title", required=True)
    description = fields.Text()
    responsible_id = fields.Many2one('res.users',
                                     ondelete='set null', string='Responsible', index=True)
    session_ids = fields.One2many('openacademy.session', 'course_id', string='Sessions')

    # _sql_constraints = [
    #     ('name_description_check',
    #      'CHECK(name != description)',
    #      'The Course Title should not be the description'),
    #
    #     ('name_unique',
    #      'UNIQUE(name)',
    #      'The Course Title must be unique')
    # ]
    _sql_constraints = [
        ('name_unique',
         'check(1=1)',
         'The Course Title must be unique')
    ]
    @api.constrains('session_ids')
    def validate_instructor(self):
        instructors = []
        for session in self.session_ids:
            instructors.append(session.instructor_id)


    @api.model
    def create(self, vals):
        print("Course Create values ", vals)
        return super(Course, self).create(vals)

    def write(self, vals):
        print("Course write values ", vals)
        return super(Course, self).write(vals)

    # (0, 0, {}) add new course with sessions
    def create_new_course(self):
        self.create({
            "name": "new course",
            "session_ids": [(0, 0, {'name': 'new session 1'}),
                            (0, 0, {'name': 'new session 2'})]
        })

    # (0, 0, {}) add session to existing record
    def add_session(self):
        self.write({"session_ids": [(0, 0, {"name": "new session"})]})

    # (1, id, {}) edit existing session
    def edit_all_sessions(self):
        sessions = {"session_ids": []}
        for session in self.session_ids:
            sessions['session_ids'].append([1, session.id, {'name': session.name + " edited"}])
        self.write(sessions)

    # (2, id, false) delete session permanently
    def delete_session(self):
        session_id = self.env['openacademy.session'].search([("course_id", "=", self.id)], limit=1).id
        print("session id ", session_id)
        if session_id:
            self.write({"session_ids": [(2, session_id, 0)]})

    # (3, id, false) unlink session
    def unlink_session(self):
        session_id = self.env['openacademy.session'].search([("course_id", "=", self.id)], limit=1).id
        print("session id ", session_id)
        if session_id:
            self.write({"session_ids": [(3, session_id)]})

    # (4, id, false) link session
    def link_session(self):
        session_id = self.env['openacademy.session'].search([("course_id", "!=", self.id)], limit=1).id
        print("session id ", session_id)
        if session_id:
            self.write({"session_ids": [(4, session_id, 0)]})

    # (5, 0, 0) delete linked sessions
    def delete_all_sessions(self):
        self.write({"session_ids": [(5, 0, 0)]})

    def delete_course(self):
        self.env['openacademy.course'].browse(self.id).unlink()

    def copy(self, default=None):
        if default is None:
            default = {}

        if not default.get('name'):
            default['name'] = self.name + " (copy)"

        return super(Course, self).copy(default)

    @api.ondelete(at_uninstall=False)
    def _unlink_except_has_sessions(self):
        for rec in self:
            if rec.session_ids:
                raise exceptions.ValidationError("You cannot delete a course with sessions")

