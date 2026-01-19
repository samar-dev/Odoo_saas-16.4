import re
from dateutil import relativedelta
from odoo import models, fields, api, _, exceptions
from odoo.exceptions import UserError


def _check_cnss_format(vat):
    if not vat:
        return "Le N° CNSS est vide"
    # VAT number format for individuals or non-companies
    if not re.match(r"^\d{8}-\d{2}$", vat):
        return "Le format du cnss est invalide.. Exemple: 12345678-02"

    return ""


def _check_vat_format(vat):
    if not vat:
        return "Le N° CIN est vide"
    # VAT number format for individuals or non-companies
    if not re.match(r"^[0-9]{8}$", vat):
        return "Le N° CIN ne respecte pas le format approprié. Exemple: 04251241"

    return ""


class EmployeeUpdate(models.Model):
    _inherit = "hr.employee"
    # Identification personnelle
    cin_issuance_date = fields.Date(
        string="Date délivrance CIN", tracking=True, groups="hr.group_hr_user"
    )
    cin_issuance_place = fields.Char(
        string="Lieu délivrance CIN", tracking=True, groups="hr.group_hr_user"
    )
    cin_scanned_file = fields.Many2many(
        "ir.attachment",
        "hr_employee_attachment_cin_rel",
        "employee_id",
        column2="attachment_id",
        string="Cin Scanné",
    )
    cnss_registration_number = fields.Char(
        string="Matricule CNSS", tracking=True, groups="hr.group_hr_user"
    )
    cnss_effective_date = fields.Date(
        string="Date d'effet CNSS", tracking=True, groups="hr.group_hr_user"
    )
    cnss_scanned_file = fields.Many2many(
        "ir.attachment",
        "hr_employee_attachment_cnss_rel",
        "employee_id",
        column2="attachment_id",
        string="CNSS Scanné",
    )

    rib_number = fields.Char(string="RIB", tracking=True, groups="hr.group_hr_user")
    rib_scanned_file = fields.Many2many(
        "ir.attachment",
        "hr_employee_attachment_rib_rel",
        "employee_id",
        column2="attachment_id",
        string="RIB Scanné",
    )
    bank_id = fields.Many2one("res.bank", string="Banque", groups="hr.group_hr_user")

    holder = fields.Boolean("Titulaire", default=False, groups="hr.group_hr_user")

    b3_scanned_file = fields.Many2many(
        "ir.attachment",
        "hr_employee_attachment_b3_rel",
        "employee_id",
        column2="attachment_id",
        string="Bulletin N°3",
    )

    # Parametres hr

    contract_type = fields.Selection(
        string="Type de contrat",
        selection=[
            ("no", "Non Spécifié"),
            ("cdi", "CDI"),
            ("cdd", "CDD"),
            ("civp_caip", "CIVP/CAIP"),
            ("karama", "Karama"),
        ],
    )
    locked = fields.Boolean("Verouillé", default=False, groups="hr.group_hr_user")
    currency_id = fields.Many2one(
        string="Monnaie", related="company_id.currency_id", readonly=True
    )
    additional_premium = fields.Monetary(
        "Primer complimentaire", tracking=True, default=0.0
    )
    disabled_child = fields.Integer(
        "Enfant infirme",
    )
    child_sup = fields.Integer("Enfant sup")
    convention_id = fields.Many2one("hr.convention", string="Convention")
    civp_amount = fields.Monetary(string="Montant CIVP", tracking=True, required=True)
    net_salary = fields.Monetary(
        string="Salaire NET",
        tracking=True,
        required=True,
    )
    gross_salary = fields.Monetary(string="Salaire BRUT", tracking=True, required=True)
    base_salary = fields.Monetary(
        string="Salaire de Base",
        tracking=True,
        required=True,
        store=True,
        compute="_compute_base_salary",
    )

    echelon_date = fields.Date(
        string="Date dernier passage d'échelon", groups="hr.group_hr_user"
    )

    nb_salary = fields.Float("Nombre Salaire")

    convention_category_id = fields.Many2one(
        "hr.convention.category", string="Echelle", groups="hr.group_hr_user"
    )
    convention_category = fields.Selection(
        string="Catégorie",
        selection=[
            ("execution", "Agent d'éxecution"),
            ("maitrise", "Maîtrise"),
            ("cadre", "Cadre"),
        ],
        tracking=True,
        groups="hr.group_hr_user",
    )
    convention_echelon = fields.Selection(
        string="Echelon",
        selection=[
            ("ech_1", "1"),
            ("ech_2", "2"),
            ("ech_3", "3"),
            ("ech_4", "4"),
            ("ech_5", "5"),
            ("ech_6", "6"),
            ("ech_7", "7"),
            ("ech_8", "8"),
            ("ech_9", "9"),
            ("ech_10", "10"),
            ("ech_11", "11"),
            ("ech_12", "12"),
            ("ech_13", "13"),
            ("ech_14", "14"),
            ("ech_15", "15"),
        ],
        tracking=True,
        groups="hr.group_hr_user",
    )
    spouse_job = fields.Char(
        string="Profession du conjoint",
        tracking=True,
    )
    fuel_card = fields.Boolean(
        string="Carte Carburant", tracking=True, groups="hr.group_hr_user"
    )
    fuel_card_number = fields.Char(
        string="N° Carte Carburant", tracking=True, groups="hr.group_hr_user"
    )
    fuel_card_rate = fields.Monetary(
        string="Forfait Carburant", tracking=True, groups="hr.group_hr_user"
    )
    toll_card = fields.Boolean(
        string="Carte Péage", tracking=True, groups="hr.group_hr_user"
    )
    toll_card_number = fields.Char(
        string="N° Carte Péage", tracking=True, groups="hr.group_hr_user"
    )
    toll_card_rate = fields.Monetary(
        string="Forfait Péage", tracking=True, groups="hr.group_hr_user"
    )
    group_insurance = fields.Boolean(
        string="Assurance Groupe", tracking=True, groups="hr.group_hr_user"
    )
    vehicle_type = fields.Selection(
        string="Type de voiture",
        selection=[("service", "Service"), ("fonction", "Fonction")],
        tracking=True,
        groups="hr.group_hr_user",
    )
    basket_allowance = fields.Monetary(
        string="Prime de panier", groups="hr.group_hr_user"
    )
    transport_allowance = fields.Monetary(
        string="Prime de Transport", groups="hr.group_hr_user"
    )
    attendance_bonus = fields.Monetary(
        string="Prime de présence", groups="hr.group_hr_user"
    )
    differential_bonus = fields.Monetary(
        string="Prime différentiel fixe", groups="hr.group_hr_user"
    )

    @api.constrains("cnss_registration_number")
    def _constraint_cnss_number(self):
        for record in self:
            validation_message = _check_cnss_format(record.cnss_registration_number)
            if (
                record.cnss_registration_number
                and not record.contract_type == "civp_caip"
            ):
                employees = self.env["hr.employee"].search(
                    [
                        (
                            "cnss_registration_number",
                            "=",
                            record.cnss_registration_number,
                        ),
                        ("id", "!=", record.id),
                        ("active", "=", True),
                    ]
                )
                if employees and len(employees) > 0:
                    raise exceptions.UserError(
                        _("Le numéro cnss doit être unique dans la base")
                    )
            if validation_message != "":
                if validation_message:
                    raise exceptions.ValidationError(validation_message)

    @api.constrains("identification_id")
    def _constraint_identification_id(self):
        for record in self:
            validation_message = _check_vat_format(record.identification_id)
            if record.identification_id:
                employees = self.env["hr.employee"].search(
                    [
                        ("identification_id", "=", record.identification_id),
                        ("id", "!=", record.id),
                        ("active", "=", True),
                    ]
                )
                if employees and len(employees) > 0:
                    raise exceptions.UserError(
                        _("Le CIN doit être unique dans la base")
                    )
                if validation_message != "":
                    if validation_message:
                        raise exceptions.ValidationError(validation_message)

    @api.constrains("rib_number")
    def _constraint_rib(self):
        for record in self:
            if record.rib_number and len(record.rib_number) != 20:
                raise exceptions.UserError(_("Le RIB doit être sur 20 chiffres"))
            employees = self.env["hr.employee"].search(
                [
                    ("rib_number", "=", record.rib_number),
                    ("id", "!=", record.id),
                    ("active", "=", True),
                ]
            )
            if employees and len(employees) > 0:
                raise exceptions.UserError(_("Le RIB doit être unique dans la base"))

    @api.onchange("convention_category")
    def onchange_convention_category(self):
        for s in self:
            return {
                "domain": {
                    "convention_category_id": [("target", "=", s.convention_category)]
                }
            }

    @api.depends("convention_category_id")
    def _compute_base_salary(self):
        for s in self:
            if (
                not s.convention_echelon
                or not s.convention_category_id
                or not s.convention_category_id.id
            ):
                s.base_salary = 0
            base_salary = self.env["hr.convention.base.salary"].search(
                [("category_id", "=", s.convention_category_id.id)]
            )
            if not base_salary:
                s.base_salary = 0
                return
            if s.convention_echelon == "ech_1":
                s.base_salary = base_salary.ech_1
            elif s.convention_echelon == "ech_2":
                s.base_salary = base_salary.ech_2
            elif s.convention_echelon == "ech_3":
                s.base_salary = base_salary.ech_3
            elif s.convention_echelon == "ech_4":
                s.base_salary = base_salary.ech_4
            elif s.convention_echelon == "ech_5":
                s.base_salary = base_salary.ech_5
            elif s.convention_echelon == "ech_6":
                s.base_salary = base_salary.ech_6
            elif s.convention_echelon == "ech_7":
                s.base_salary = base_salary.ech_7
            elif s.convention_echelon == "ech_8":
                s.base_salary = base_salary.ech_8
            elif s.convention_echelon == "ech_9":
                s.base_salary = base_salary.ech_9
            elif s.convention_echelon == "ech_10":
                s.base_salary = base_salary.ech_10
            elif s.convention_echelon == "ech_11":
                s.base_salary = base_salary.ech_11
            elif s.convention_echelon == "ech_12":
                s.base_salary = base_salary.ech_12
            elif s.convention_echelon == "ech_13":
                s.base_salary = base_salary.ech_13
            elif s.convention_echelon == "ech_14":
                s.base_salary = base_salary.ech_14
            else:
                s.base_salary = base_salary.ech_15

    def lock(self):
        for s in self:
            s.write({"locked": True})

    def unlock(self):
        for s in self:
            s.write({"locked": False})

    @api.constrains("pin")
    def _constraint_matricule(self):
        for record in self:
            if record.pin:
                employees = self.env["hr.employee"].search(
                    [("pin", "=", record.pin), ("id", "!=", record.id)]
                )
                if employees and len(employees) > 0:
                    raise UserError(_("La Matricule doit être unique dans la base"))

    def _passage_echelon(self):
        return True
