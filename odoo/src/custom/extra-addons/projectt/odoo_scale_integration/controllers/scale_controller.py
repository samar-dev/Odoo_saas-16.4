# controllers/scale_controller.py
from odoo import http
from odoo.http import request


class ScaleController(http.Controller):
    @http.route(
        "/scale/read", type="json", auth="public", methods=["POST"], website=True
    )
    def read_scale(self):
        reader = request.env["scale.reader"].create({})
        weight = reader.read_weight()
        if weight is not None:
            return {"weight": weight}
        return {"error": "Failed to read weight"}
