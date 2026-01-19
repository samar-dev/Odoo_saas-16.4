from odoo import models, fields

class WizardAccountMoveLineDescription(models.TransientModel):
    _name = 'wizard.account.move.line.description'
    _description = 'Add Description to Account Move Line'

    move_line_id = fields.Many2one(
        'account.move.line',
        string='Move Line',
        required=True
    )

    description = fields.Char(string="Description", required=True)

    def apply_description(self):
        self.ensure_one()
        self.move_line_id.extra_description = self.description
        return {'type': 'ir.actions.act_window_close'}


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    extra_description = fields.Char(string="Extra Description")
    def open_description_wizard(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Add Description',
            'res_model': 'wizard.account.move.line.description',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_move_line_id': self.id,
            }
        }



