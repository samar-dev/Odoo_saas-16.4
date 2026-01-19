from odoo import http
from odoo.addons.web.controllers.dataset import DataSet
from odoo.http import request
from odoo.osv import expression


class DataAccessGuardController(DataSet):
    def _call_kw(self, model, method, args, kwargs):
        if method == "name_search":
            current_user = request.env.user
            model_id = request.env["ir.model"].sudo().search([("model", "=", model)])
            access_rules = request.env["data.access.guard"].search(
                [("model_id", "=", model_id.id)]
            )
            for rule in access_rules.filtered(lambda r: current_user in r.user_ids):
                temp_args = kwargs.get("args", [])
                temp_args = expression.AND([rule._get_raw_domain(), temp_args])
                kwargs["args"] = temp_args

        res = super(DataAccessGuardController, self)._call_kw(
            model, method, args, kwargs
        )
        return res

    @http.route("/web/dataset/search_read", type="json", auth="user")
    def search_read(
        self, model, fields=False, offset=0, limit=False, domain=None, sort=None
    ):
        domain = domain or []
        current_user = request.env.user
        model_id = request.env["ir.model"].sudo().search([("model", "=", model)])
        access_rules = request.env["data.access.guard"].search(
            [("model_id", "=", model_id.id)]
        )
        for rule in access_rules.filtered(lambda r: current_user in r.user_ids):
            domain = expression.AND([rule._get_raw_domain(), domain])
        res = super(DataAccessGuardController, self).search_read(
            model, fields, offset, limit, domain, sort
        )
        return res
