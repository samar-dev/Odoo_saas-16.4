# -*- coding: utf-8 -*-

from odoo import models, fields


class HrConvention(models.Model):
    _name = "hr.convention"

    name = fields.Char(string="Intitulé")
    regime = fields.Integer(string="Régime(heures)")
    category_ids = fields.One2many(
        "hr.convention.category", "convention_id", string="Catégories"
    )
    base_salary_line_ids = fields.One2many(
        "hr.convention.base.salary", "convention_id", string="Salaires de base"
    )


class HrConventionCategory(models.Model):
    _name = "hr.convention.category"

    name = fields.Char(string="Intitulé", required=True)
    target = fields.Selection(
        string="Catégorie",
        selection=[
            ("cadre", "Cadre"),
            ("maitrise", "Maîtrise"),
            ("execution", "Agent d'éxecution"),
        ],
        tracking=True,
        required=True,
    )
    convention_id = fields.Many2one("hr.convention", string="Convention")


class HrConventionBaseSalary(models.Model):
    _name = "hr.convention.base.salary"

    convention_id = fields.Many2one("hr.convention", string="Convention")
    category_id = fields.Many2one("hr.convention.category", string="Catégorie")
    ech_1 = fields.Float(string="Ech1", required=True, digits=(5, 3))
    ech_2 = fields.Float(string="Ech2", required=True, digits=(5, 3))
    ech_3 = fields.Float(string="Ech3", required=True, digits=(5, 3))
    ech_4 = fields.Float(string="Ech4", required=True, digits=(5, 3))
    ech_5 = fields.Float(string="Ech5", required=True, digits=(5, 3))
    ech_6 = fields.Float(string="Ech6", required=True, digits=(5, 3))
    ech_7 = fields.Float(string="Ech7", required=True, digits=(5, 3))
    ech_8 = fields.Float(string="Ech8", required=True, digits=(5, 3))
    ech_9 = fields.Float(string="Ech9", required=True, digits=(5, 3))
    ech_10 = fields.Float(string="Ech10", required=True, digits=(5, 3))
    ech_11 = fields.Float(string="Ech11", required=True, digits=(5, 3))
    ech_12 = fields.Float(string="Ech12", required=True, digits=(5, 3))
    ech_13 = fields.Float(string="Ech13", required=True, digits=(5, 3))
    ech_14 = fields.Float(string="Ech14", required=True, digits=(5, 3))
    ech_15 = fields.Float(string="Ech15", required=True, digits=(5, 3))
