from odoo import fields, models, api, exceptions, _
from datetime import timedelta

class Session(models.Model):
    _name = 'openacademy.session'
    _description = 'Open Academy Session'

    name = fields.Char(required=True)
    start_date = fields.Date(default=fields.Date.today)

    # 1111.11 6 total digits two after the digits
    duration = fields.Float(digits=(6, 2), help="Duration in days")
    seats = fields.Integer(string="Number of seats")
    active = fields.Boolean(default=True)
    end_date = fields.Date(string="End Date", store=True,
                           compute="_get_end_date", inverse="_set_end_date")

    instructor_id = fields.Many2one('res.partner', string='Instructor')
    course_id = fields.Many2one('openacademy.course', string='Course')
    attendee_ids = fields.Many2many('res.partner', string="Attendees")
    attendees_count = fields.Integer(string="Attendees Count", store=True,
                                     compute="_get_attendees_count")
    taken_seats = fields.Float(string="Taken Seats", compute='_taken_seats')

    # @api.constrains('instructor_id')
    # def check_instructor_id(self):
    #     instructor_ids = self.env['openacademy.session'].search([]).instructor_id
    #     if self.instructor_id in instructor_ids:
    #         raise exceptions.ValidationError("instructor is duplicated")


    @api.depends('attendee_ids')
    def _get_attendees_count(self):
        for r in self:
            r.attendees_count = len(r.attendee_ids)

    @api.depends('start_date', 'duration')
    def _get_end_date(self):
        for r in self:
            if not (r.start_date and r.duration):
                r.end_date = r.start_date
                continue

            duration = timedelta(days=r.duration, seconds=-1)
            r.end_date = r.start_date + duration

    def _set_end_date(self):
        for r in self:
            if not (r.start_date and r.end_date):
                continue
            r.duration = (r.end_date - r.start_date).days + 1

    @api.depends('seats','attendee_ids')
    def _taken_seats(self):
        for r in self:
            if not r.seats:
                r.taken_seats = 0.0
            else :
                r.taken_seats = 100.0 * (len(r.attendee_ids) / r.seats)

    @api.onchange('seats','attendee_ids')
    def verify_valid_seats(self):
        if self.seats < 0:
            return {
                'warning': {
                    'title': _("Incorrect 'seats' value"),
                    'message': _("The number of available seats may not be negative")
                }
            }
        if self.seats < len(self.attendee_ids):
            return {
                'warning': {
                    'title': _("too many attendees"),
                    'message': _("Increase seats or remove attendees")
                }
            }

        @api.constrains('instructor_id', 'attendee_ids')
        def _check_instructor_not_in_attendees(self):
            print("im here2")
            for r in self:
                if r.instructor_id and r.instructor_id in r.attendee_ids:
                    raise exceptions.ValidationError(_("A session's instructor cannot be an attendee"))
