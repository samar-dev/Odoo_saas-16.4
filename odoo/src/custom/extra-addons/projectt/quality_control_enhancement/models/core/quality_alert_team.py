from odoo import fields, models


class QualityAlertTeam(models.Model):
    _inherit = "quality.alert.team"

    failed_check_count = fields.Integer(
        "# Failed Checks", compute="_compute_check_count"
    )
    success_check_count = fields.Integer(
        "# Success Checks", compute="_compute_check_count"
    )
    validated_check_count = fields.Integer(
        "# Validated Checks", compute="_compute_check_count"
    )

    def _compute_check_count(self):
        super()._compute_check_count()

        # compute failed_check_count
        failed_check_data = self.env["quality.check"]._read_group(
            [("team_id", "in", self.ids), ("quality_state", "=", "fail")],
            ["team_id"],
            ["__count"],
        )
        failed_check_result = {team.id: count for team, count in failed_check_data}

        # compute success_check_count
        success_check_data = self.env["quality.check"]._read_group(
            [("team_id", "in", self.ids), ("quality_state", "=", "pass")],
            ["team_id"],
            ["__count"],
        )
        success_check_result = {team.id: count for team, count in success_check_data}

        # compute validated_check_count
        validated_check_data = self.env["quality.check"]._read_group(
            [("team_id", "in", self.ids), ("quality_state", "=", "validated")],
            ["team_id"],
            ["__count"],
        )
        validated_check_result = {
            team.id: count for team, count in validated_check_data
        }

        for team in self:
            team.failed_check_count = failed_check_result.get(team.id, 0)
            team.success_check_count = success_check_result.get(team.id, 0)
            team.validated_check_count = validated_check_result.get(team.id, 0)
