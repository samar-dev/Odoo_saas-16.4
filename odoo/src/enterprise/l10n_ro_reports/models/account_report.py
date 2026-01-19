# -*- coding: utf-8 -*-
"""
Part of Odoo. See LICENSE file for full copyright and licensing details.
"""

from odoo import models


class ReportAccountFinancialReport(models.AbstractModel):
    _name = "l10n_ro.report.handler"
    _inherit = "account.report.custom.handler"
    _description = "Report custom handler for romanian financial reports"

    # Class will be removed in master
    def _custom_options_initializer(self, report, options, previous_options=None):
        super()._custom_options_initializer(report, options, previous_options=previous_options)
