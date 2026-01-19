from odoo import api, fields, models, _
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
_logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# HELP DESK TEAM
# ---------------------------------------------------------

class HelpdeskTeam(models.Model):
    _inherit = 'helpdesk.team'
    _order = "sequence, id"

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )

    alias_id_seconds = fields.One2many(
        'helpdesk.alias.member',
        'team_id',
        string='Alias Members',
    )


    smtp_server = fields.Char(string="SMTP Server", default="smtp.gmail.com")
    smtp_port = fields.Integer(string="SMTP Port", default=587)
    smtp_user = fields.Char(string="SMTP User")
    smtp_password = fields.Char(string="SMTP Password")

    # -----------------------------
    # Send emails to alias members
    # -----------------------------

    def send_email_to_alias_members(
            self,
            subject,
            body,
            smtp_server=None,
            smtp_port=None,
            smtp_user=None,
            smtp_password=None,
    ):
        """
        Send an email to all employees linked via alias_id_seconds > employee_ids
        using SMTP, posting detailed success/failure messages in team chatter.
        """
        self.ensure_one()

        # Gather all valid emails
        emails = list({
            e.work_email.strip()
            for alias in self.alias_id_seconds
            for e in alias.employee_ids
            if e.work_email and "@" in e.work_email
        })

        if not emails:
            message = f"No valid emails found for team '{self.name}'. Email not sent."
            self.message_post(body=message, subtype_xmlid='mail.mt_note')
            return False

        # Use team fields if not passed
        smtp_server = smtp_server or self.smtp_server
        smtp_port = smtp_port or self.smtp_port or 587
        smtp_user = smtp_user or self.smtp_user or self.env.user.email
        smtp_password = smtp_password or self.smtp_password

        if not smtp_user or not smtp_password:
            msg = f"SMTP credentials not set for team '{self.name}'. Email not sent."
            self.message_post(body=msg, subtype_xmlid='mail.mt_note')
            return False

        # Build email
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = ", ".join(emails)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, emails, msg.as_string())
            server.quit()

            message = f"Email sent successfully to: {', '.join(emails)}"
            self.message_post(body=message, subtype_xmlid='mail.mt_note')
            return True

        except smtplib.SMTPAuthenticationError as auth_err:
            # Specific message for Office 365 / Outlook blocked accounts
            err_msg = str(auth_err)
            if "5.7.139" in err_msg or "Authentication unsuccessful" in err_msg:
                message = (
                    f"Failed to send email for team '{self.name}': "
                    "Authentication unsuccessful. "
                    "If using Outlook/Office 365, generate an App Password or contact your administrator."
                )
            else:
                message = f"Failed to send email for team '{self.name}': {err_msg}"

            _logger.error("SMTP auth error for team %s: %s", self.name, auth_err)
            self.message_post(body=message, subtype_xmlid='mail.mt_note')
            return False

        except Exception as e:
            _logger.error("SMTP error for team %s: %s", self.name, e)
            message = f"Failed to send email for team '{self.name}': {str(e)}"
            self.message_post(body=message, subtype_xmlid='mail.mt_note')
            return False

    # -----------------------------
    # Override create
    # -----------------------------
    def create(self, vals):
        team = super().create(vals)

        if team.alias_id_seconds:
            subject = f"New Helpdesk Team Created: {team.name}"
            body = f"<p>The helpdesk team <strong>{team.name}</strong> has been created.</p>"
            team.send_email_to_alias_members(
                subject,
                body,
                smtp_server=team.smtp_server,
                smtp_port=team.smtp_port,
                smtp_user=team.smtp_user,
                smtp_password=team.smtp_password
            )

        return team

    # -----------------------------
    # Override write
    # -----------------------------
    def write(self, vals):
        res = super().write(vals)

        for team in self:
            if team.alias_id_seconds:
                subject = f"Helpdesk Team Updated: {team.name}"
                body = f"<p>The helpdesk team <strong>{team.name}</strong> has been updated.</p>"
                team.send_email_to_alias_members(
                    subject,
                    body,
                    smtp_server=team.smtp_server,
                    smtp_port=team.smtp_port,
                    smtp_user=team.smtp_user,
                    smtp_password=team.smtp_password
                )

        return res


    # -----------------------------
    # Handle incoming emails
    # -----------------------------
    @api.model
    def message_new(self, msg, custom_values=None):
        """
        Handle incoming email to a helpdesk team alias.
        Posts message in chatter and subscribes the sender if a partner exists.
        """
        if custom_values is None:
            custom_values = {}

        alias_email = (msg.get('to') or '').split('@')[0].strip()
        team = self.search([('alias_name', '=', alias_email)], limit=1)

        if not team:
            return super().message_new(msg, custom_values=custom_values)

        subject = msg.get('subject') or _('No Subject')
        body = msg.get('body') or _('No body content found.')

        team.message_post(
            subject=subject,
            body=body,
            subtype_xmlid='mail.mt_comment',
        )

        sender_email = msg.get('from')
        if sender_email:
            partner = self.env['res.partner'].sudo().search([('email', '=', sender_email)], limit=1)
            if partner:
                team.message_subscribe([partner.id])
                team.message_post(body=f"Subscribed sender: {partner.name}", subtype_xmlid='mail.mt_note')
            else:
                team.message_post(body=f"No partner found for sender: {sender_email}", subtype_xmlid='mail.mt_note')
        else:
            team.message_post(body="Incoming email had no sender.", subtype_xmlid='mail.mt_note')

        return team





# ---------------------------------------------------------
# ALIAS MEMBER
# ---------------------------------------------------------
class HelpdeskAliasMember(models.Model):
    _name = 'helpdesk.alias.member'
    _description = 'Helpdesk Alias Member'

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        ondelete='cascade',
    )

    name = fields.Char(string="Name")

    employee_ids = fields.Many2many(
        'hr.employee',
        'employee_report_rel',     # relation table
        'report_id',               # column for this model
        'employee_id',             # column for hr.employee
        string='Employees',
        required=True,
        default=lambda self: self._get_all_employees_default(),
    )

    email = fields.Char(
        string='Email',
        related='employee_id.work_email',
        readonly=True,
    )

    team_id = fields.Many2one(
        'helpdesk.team',
        string='Helpdesk Team',
        ondelete='cascade',
        required=True,
    )

    active = fields.Boolean(string='Active', default=True)

    # -----------------------------------------------------
    # DEFAULT: all employees
    # -----------------------------------------------------
    @api.model
    def _get_all_employees_default(self):
        employees = self.env['hr.employee'].sudo().search([])
        return employees.ids
