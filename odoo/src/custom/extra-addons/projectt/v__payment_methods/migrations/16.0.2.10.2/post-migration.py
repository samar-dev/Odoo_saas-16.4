from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    stages = env["account.payment.method.stage"].search([("type", "=", "default")])
    stages.write({"type": None})
