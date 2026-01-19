from odoo.addons.web.controllers.dataset import DataSet
from odoo.exceptions import AccessError
from odoo.http import request


class MethodAccessGuardController(DataSet):
    def _call_kw(self, model, method, args, kwargs):
        current_user = request.env.user
        model_id = request.env["ir.model"].sudo().search([("model", "=", model)])
        access_rules = (
            request.env["method.access.guard"]
            .search([("model_id", "=", model_id.id), ("method_name", "=", method)])
            .sorted("type")
        )
        for rule in access_rules:
            if rule.type == "blacklist" and current_user in rule.blacklisted_user_ids:
                raise AccessError(rule.message)
            elif (
                rule.type == "whitelist"
                and current_user not in rule.whitelisted_user_ids
            ):
                raise AccessError(rule.message)

        res = super(MethodAccessGuardController, self)._call_kw(
            model, method, args, kwargs
        )
        return res
