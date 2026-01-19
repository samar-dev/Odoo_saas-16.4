from odoo import models, fields, api
class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    # --------------------------
    # Helper: get correct work entry type
    # --------------------------
    def _get_leave_work_entry_type(self, leave):
        """Return correct work entry type for this leave."""
        if leave.holiday_status_id.work_entry_type_id:
            return leave.holiday_status_id.work_entry_type_id

        WorkEntryType = self.env['hr.work.entry.type']

        if leave.holiday_status_id.unpaid:
            return WorkEntryType.search([('code', '=', 'LEAVE110')], limit=1)

        return WorkEntryType.search([('code', '=', 'LEAVE120')], limit=1)

    # --------------------------
    # Override worked day lines
    # --------------------------
    def _get_worked_day_lines(self, domain=None, check_out_of_contract=True):
        # Original Odoo lines
        res = super()._get_worked_day_lines(domain=domain, check_out_of_contract=check_out_of_contract)

        # Group lines by work_entry_type_id
        grouped = {}
        leave_codes = ('LEAVE110', 'LEAVE120')  # leave types to remain untouched
        leave_types = set()

        for line in res:
            key = line['work_entry_type_id']
            work_entry = self.env['hr.work.entry.type'].browse(key)

            if key not in grouped:
                grouped[key] = line.copy()
            else:
                grouped[key]['number_of_days'] += line['number_of_days']
                grouped[key]['number_of_hours'] += line['number_of_hours']

            if work_entry.code in leave_codes:
                leave_types.add(key)

        # Extra Sunday logic from hr.leave
        for slip in self:
            employee = slip.employee_id
            contract = slip.contract_id
            hours_per_day = contract.resource_calendar_id.hours_per_day

            leaves = self.env["hr.leave"].search([
                ('employee_id', '=', employee.id),
                ('state', '=', 'validate'),
                ('request_date_from', '>=', slip.date_from),
                ('request_date_to', '<=', slip.date_to),
            ])

            for leave in leaves:
                holiday_companies = leave.holiday_status_id.company_ids.ids
                if holiday_companies and employee.company_id.id not in holiday_companies:
                    continue

                base_days = leave.number_of_days  # already includes extra Sundays
                work_entry_type = slip._get_leave_work_entry_type(leave)
                if not work_entry_type:
                    continue

                key = work_entry_type.id
                leave_types.add(key)

                if key not in grouped:
                    grouped[key] = {
                        'sequence': work_entry_type.sequence,
                        'work_entry_type_id': work_entry_type.id,
                        'number_of_days': base_days,
                        'number_of_hours': base_days * hours_per_day,
                    }
                else:
                    grouped[key]['number_of_days'] = base_days
                    grouped[key]['number_of_hours'] = base_days * hours_per_day

                g= grouped

        # ---------------------------
        # Cap only non-leave worked days
        # ---------------------------
        max_days = 26
        max_hours = 208


        # Calculate total leave days/hours from leave records
        total_leave_days = sum(leave.number_of_days for leave in leaves)
        total_leave_hours = sum(leave.number_of_days * hours_per_day for leave in leaves)

        # Remaining allowed worked days/hours
        allowed_non_leave_days = max(max_days - total_leave_days, 0)
        allowed_non_leave_hours = max(max_hours - total_leave_hours, 0)

        # Sum of non-leave lines
        non_leave_days = sum(line['number_of_days'] for key, line in grouped.items() if key not in leave_types)
        non_leave_hours = sum(line['number_of_hours'] for key, line in grouped.items() if key not in leave_types)

        # Scale only if non-leave lines exceed allowed remaining
        if non_leave_days > allowed_non_leave_days or non_leave_hours > allowed_non_leave_hours:
            scale_days = allowed_non_leave_days / non_leave_days if non_leave_days > 0 else 0
            scale_hours = allowed_non_leave_hours / non_leave_hours if non_leave_hours > 0 else 0
            scale = min(scale_days, scale_hours)

            for key, line in grouped.items():
                if key not in leave_types:
                    line['number_of_days'] = round(line['number_of_days'] * scale, 2)
                    line['number_of_hours'] = round(line['number_of_hours'] * scale, 2)

        return list(grouped.values())

    @api.onchange('worked_days_line_ids')
    def _onchange_worked_days_line_ids(self):
        """Recompute number_of_hours whenever worked_days_line_ids changes"""
        for slip in self:
            for line in slip.worked_days_line_ids:
                if line.number_of_days :
                    line.number_of_hours = line.number_of_days * 8
                else:
                    line.number_of_hours = 0
