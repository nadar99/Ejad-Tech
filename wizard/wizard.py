from odoo import fields, models, api


class Wizard(models.TransientModel):
    _name = 'openacademy.wizard'
    _description = 'Wizard: quick registration of attendees to sessions'

    # def _default_session(self):
    #     return self.env['openacademy.session'].browse(self._context.get('active_id'))

    def _default_sessions(self):
        return self.env['openacademy.session'].browse(self._context.get('active_ids'))

    # session_id = fields.Many2one('openacademy.session',
    #                               string="Session", required=True, default=_default_session)
    session_ids = fields.Many2many('openacademy.session',
                                  string="Sessions", required=True, default=_default_sessions)


    attendee_ids = fields.Many2many('res.partner', string="Attendees")

    # def subscribe(self):
    #     self.session_id.attendee_ids |= self.attendee_ids
    #     return {}
    #
    def subscribe(self):
        for session in self.session_ids :
            session.attendee_ids |= self.attendee_ids
        return {}