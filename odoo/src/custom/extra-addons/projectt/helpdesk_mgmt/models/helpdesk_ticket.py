
from odoo import _, api, fields, models, tools

class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    sequence = fields.Char('Sequence',default="/" , readonly=True)

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        compute='_compute_employee_id',
        store=True,  # optionnel, si tu veux stocker la valeur dans la base
        readonly=False
    )

    user_id = fields.Many2one(
        'res.users', string='Assigned to', compute='_compute_user_and_stage_ids', store=True,
        readonly=False, tracking=True,
        domain=lambda self: [('groups_id', 'in', self.env.ref('helpdesk.group_helpdesk_manager').id)])

    @api.onchange('name')
    def _compute_user_and_stage_ids(self):
        """Compute default user and stage for ticket"""
        group_manager = self.env.ref('helpdesk.group_helpdesk_manager')

        for ticket in self.filtered(lambda t: t.team_id):
            # -----------------------------
            # Assign user filtered by login containing 'alimi'
            # -----------------------------
            managers = group_manager.users.filtered(lambda u: 'alimi' in (u.login or '').lower())
            if managers:
                ticket.user_id = managers[0]  # premier manager trouvé

            # -----------------------------
            # Assign stage
            # -----------------------------
            if not ticket.stage_id or ticket.stage_id not in ticket.team_id.stage_ids:
                ticket.stage_id = ticket.team_id._determine_stage()[ticket.team_id.id]

    @api.onchange('name')  # facultatif, dépendances
    def _compute_employee_id(self):
        for ticket in self:
            # cherche l'employé lié à l'utilisateur connecté
            employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.uid)], limit=1)
            ticket.employee_id = employee or False  # ⚠️ toujours assigner un record ou False
            ticket.partner_phone = ticket.employee_id.mobile_phone




    @api.model
    def create(self, vals):

        if vals.get('sequence', '/') == '/':
            vals['sequence'] = self.env['ir.sequence'].next_by_code('seq.helpdesk.ticket') or '/'
        ticket = super(HelpdeskTicket, self).create(vals)
        # -----------------------------
        # Assign manager filtered by login containing 'alimi'
        # -----------------------------
        if ticket.team_id:
            group_manager = self.env.ref('helpdesk.group_helpdesk_manager')
            managers = group_manager.users.filtered(lambda u: 'alimi' in (u.login or '').lower())
            if managers:
                ticket.user_id = managers[0]

            # Assign stage if not set
            if not ticket.stage_id or ticket.stage_id not in ticket.team_id.stage_ids:
                ticket.stage_id = ticket.team_id._determine_stage()[ticket.team_id.id]

        # -----------------------------
        # Create activity for employee_id
        # -----------------------------
        if ticket.user_id and ticket.stage_id:
            self.env['mail.activity'].sudo().create({
                'res_model_id': self.env['ir.model']._get(ticket._name).id,
                'res_id': ticket.id,
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'summary': _('New ticket created with stage %s') % ticket.stage_id.name,
                'user_id': ticket.user_id.id if ticket.user_id else False,
                'note': _('A new helpdesk ticket <b>%s</b> has been created and assigned stage <b>%s</b>.') % (
                    ticket.name, ticket.stage_id.name
                ),
                'date_deadline': fields.Date.today(),
            })

        return ticket

    def write(self, vals):
        """Override write to create an activity when stage changes"""
        old_stages = {ticket.id: ticket.stage_id for ticket in self}
        res = super().write(vals)

        if 'stage_id' in vals:
            for ticket in self:
                old_stage = old_stages.get(ticket.id)
                new_stage = ticket.stage_id
                if old_stage != new_stage and ticket.employee_id:
                    self.env['mail.activity'].sudo().create({
                        'res_model_id': self.env['ir.model']._get(ticket._name).id,
                        'res_id': ticket.id,
                        'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                        'summary': _('Ticket stage changed to %s') % new_stage.name,
                        'user_id': ticket.employee_id.user_id.id if ticket.employee_id.user_id else False,
                        'note': _('The stage of ticket <b>%s</b> has changed from <b>%s</b> to <b>%s</b>.') % (
                            ticket.name, old_stage.name if old_stage else 'N/A', new_stage.name
                        ),
                        'date_deadline': fields.Date.today(),
                    })
        return res



