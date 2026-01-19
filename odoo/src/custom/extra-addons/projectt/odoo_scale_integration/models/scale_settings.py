from odoo import models, fields


class ScaleSettings(models.Model):
    _name = "scale.settings"
    _description = "Scale Settings"

    name = fields.Char(string="Scale Name", required=True)
    ip_address = fields.Char(string="IP Address", required=True)
    port = fields.Integer(string="Port", required=True, default=9600)

    @classmethod
    def get_settings(cls):
        settings = cls.search([], limit=1)
        if settings:
            return settings
        else:
            return cls.create(
                {"name": "Default Scale", "ip_address": "127.0.0.1", "port": 9600}
            )
