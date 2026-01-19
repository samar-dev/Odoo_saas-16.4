from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta
from pytz import timezone
import pytz


class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    # New field to specify which companies this leave type applies to
    company_ids = fields.Many2many(
        'res.company', string='Société(s)',
        help='Leave type only applies to selected companies.'
    )

    can_notify = fields.Boolean(
        string="Send Notifications",
        default=True,
        help="If disabled, no email/message notification will be sent to the employee."
    )


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    @api.depends('request_date_from', 'request_date_to', 'employee_id', 'holiday_status_id', 'request_unit_half')
    def _compute_number_of_days_display(self):
        """Compute displayed number of days, adding Sunday only if leave includes Saturday
           and the leave type is assigned to the employee's company.
           If Sunday is included but employee's company is not in leave type companies,
           subtract 1 day.
           Only applies if request_unit_half is not set.
        """
        for leave in self:
            # Skip computation if request_unit_half is set
            if leave.request_unit_half:
                leave.number_of_days_display = leave.number_of_days or 0
                continue

            # Reset days if no dates
            if not (leave.request_date_from and leave.request_date_to):
                leave.number_of_days_display = 0
                leave.number_of_days = 0
                continue

            # Base number of days
            number_of_days = (leave.request_date_to - leave.request_date_from).days + 1
            extra_days = 0

            holiday_companies = leave.holiday_status_id.company_ids.ids if leave.holiday_status_id else []
            employee_company_id = leave.employee_id.company_id.id

            # Check if Saturday is included
            saturdays_included = any(
                (leave.request_date_from + timedelta(days=i)).weekday() == 5
                for i in range(number_of_days)
            )

            # Check if Sunday is included
            sundays_included = any(
                (leave.request_date_from + timedelta(days=i)).weekday() == 6
                for i in range(number_of_days)
            )

            if employee_company_id in holiday_companies:
                # Only add extra Sunday if Saturday is included and Sunday not already in leave
                if saturdays_included and not sundays_included:
                    extra_days += 1
            else:
                # If Sunday is already included but company is NOT in holiday_companies, subtract 1 day
                if sundays_included:
                    number_of_days -= 1
                    # Ensure we don't go below 0
                    if number_of_days < 0:
                        number_of_days = 0

            leave.number_of_days_display = number_of_days + extra_days
            leave.number_of_days = number_of_days + extra_days

    def action_approve(self):
        """Override approval + custom validation + Sunday logic"""
        # --- Custom approval rights ---
        self._check_custom_leave_validation_rights()

        # --- Validation: leave must be confirmed ---
        if any(
                holiday.state not in ['confirm', 'validate1']
                and holiday.validation_type != 'no_validation'
                for holiday in self
        ):
            raise UserError(_('Time off request must be confirmed in order to approve it.'))

        # --- Call super ---
        res = super(HrLeave, self).action_approve()

        # --- Recompute days ---
        for leave in self:
            leave._compute_number_of_days_display()

        # --- Notifications (if allowed) ---
        for holiday in self.filtered(lambda h: h.employee_id.user_id):
            if not holiday.holiday_status_id.can_notify:
                continue

            user_tz = timezone(holiday.tz)
            utc_tz = pytz.utc.localize(holiday.date_from).astimezone(user_tz)

            notify_partner_ids = (
                holiday.employee_id.user_id.partner_id.ids
                if holiday.validation_type != 'both'
                else []
            )

            holiday.message_post(
                body=_(
                    'Your %(leave_type)s planned on %(date)s has been accepted',
                    leave_type=holiday.holiday_status_id.display_name,
                    date=utc_tz.replace(tzinfo=None)
                ),
                partner_ids=notify_partner_ids
            )

        return res

    def _check_custom_leave_validation_rights(self):
        current_user = self.env.user

        EXCLUDED_USER_IDS = [2, 57, 58]

        # Get employee related to current user
        current_employee = self.env['hr.employee'].search([
            ('user_id', '=', current_user.id)
        ], limit=1)

        if self.env.user.id not in EXCLUDED_USER_IDS:
            for leave in self:
                employee = leave.employee_id
                leave_manager = employee.leave_manager_id
                contract_responsible = employee.contract_id.hr_responsible_id if employee.contract_id else False
                if current_employee not in (leave_manager, contract_responsible):
                    raise UserError(_(
                        "Vous n'êtes pas autorisé à approuver ce congé.\n"
                        "Approbateurs autorisés :\n"
                        "  1) Responsable du congé de l'employé : %s\n"
                        "  2) Responsable RH du contrat : %s"
                    ) % (

                                        leave_manager.name if leave_manager else "Non défini",
                                        contract_responsible.name if contract_responsible else "Non défini",
                                    ))

