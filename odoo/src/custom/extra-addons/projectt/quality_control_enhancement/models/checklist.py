from odoo import models, fields


class QualityChecklist(models.Model):
    _name = 'quality.checklist.emballage'
    _description = 'Checklist de Contrôle à la Réception (Emballage)'

    name = fields.Char(
        string="Numéro de séquence",
        required=True,
        index=True,
        copy=False,
        readonly=True,
        default=lambda self: self.env["ir.sequence"].next_by_code(
            "checklist.emballage.sequence"
        ),
    )

    quality_check_id = fields.Many2one(
        'quality.check',
        string='Contrôle de qualité',
        ondelete='cascade',
    )
    reception_date = fields.Date('Date de réception')
    document_number = fields.Char('Numéro document')
    quantity = fields.Integer('Quantité')
    supplier = fields.Char('Fournisseur')
    articles = fields.Many2one("product.product", string="Produit")

    # Magasin
    cmd_delivery_match = fields.Boolean('Correspondance commande – livraison')
    packaging_marking_correct = fields.Boolean('Marquage correct de l\'emballage')
    delivered_on_time = fields.Boolean('Livraison dans les délais')
    proper_transport = fields.Boolean('Propreté du moyen de transport')
    unopened_clean_packaging = fields.Boolean('Emballages non entamés, exempts de souillures')
    protected_merchandise = fields.Boolean('Marchandises protégées et emballées')
    no_dust_or_humidity = fields.Boolean('Absence de poussière, humidité')
    no_smell_or_soiling = fields.Boolean('Odeur, aspect extérieur, souillures')

    # Qualité - Étiquette
    label_print_quality = fields.Boolean('Impression lisible et ajustée')
    label_dimensions = fields.Boolean('Dimension / forme de découpe')
    label_bat = fields.Boolean('Conforme au BAT')
    label_bobine = fields.Boolean('État bobine (sens, diamètre)')

    # Carton / Séparation
    carton_print_quality = fields.Boolean('Impression lisible')
    carton_dimensions = fields.Boolean('Dimension correcte')
    carton_shape = fields.Boolean('Forme de découpe')
    carton_material_state = fields.Boolean('État de la matière')

    # Bidon / Bouteille
    bottle_material_state = fields.Boolean('État de la matière (Résistance de la Bouteille)')
    bottle_sealing = fields.Boolean('Sertissage et soudure')
    bottle_color = fields.Boolean('Couleur et cristallisation')
    bottle_volume = fields.Boolean('Volume / dimensions')
    bottle_repair = fields.Boolean('Réparation du soufflage')

    # Manchon
    sleeve_print = fields.Boolean('Impression')
    sleeve_perforation = fields.Boolean('Perforation complète')
    sleeve_shrink = fields.Boolean('Rétraction / qualité support')
    sleeve_dimensions = fields.Boolean('Dimensions')

    # Conformité
    conformity = fields.Selection([
        ('conforme', 'Conforme'),
        ('non_conforme', 'Non Conforme')
    ], string="Conformité générale")

    decision = fields.Selection([
        ('accepted', 'Acceptée'),
        ('accepted_with_derogation', 'Acceptée avec dérogation'),
        ('refused', 'Refusée')
    ], string="Décision")

    comments = fields.Text("Commentaire")

    aroma = fields.Char('Arôme / vinaigre')
    dlc = fields.Boolean('DLC')
    color = fields.Boolean('Couleur')
    odor = fields.Boolean('Odeur')
    solubility = fields.Boolean('Solubilité')

    certificate_present = fields.Boolean('Certificat d\'alimentarité ou de conformité présent')

    visa_stock = fields.Char('Visa responsable stock')
    visa_quality = fields.Char('Visa responsable qualité')

    # Réception huile olive

    producteur = fields.Char(string="Producteur")

    numero_lot = fields.Char(string="N° Lot")
    matricule_camion = fields.Char(string="Matricule Camion")
    numero_facture = fields.Char(string="N° Facture")
    numero_bon_pesage = fields.Char(string="N° Bon de Pesage")
    emplacement = fields.Char(string="Emplacement")

    numero_admin = fields.Char(string="N° Administratif")
    numero_rapport_analyse = fields.Char(string="N° Rapport d’Analyse")

    # Contrôle à la réception
    proprete_citerne = fields.Selection([('c', 'Conforme'), ('nc', 'Non Conforme')], string="Propreté Citerne Stockage")
    citerne_vide = fields.Boolean(string="Citerne Vide")
    citerne_sans_odeur = fields.Boolean(string="Sans Odeur")
    citerne_humide = fields.Boolean(string="Humidité")
    proprete_conduites = fields.Selection([('c', 'Conforme'), ('nc', 'Non Conforme')], string="Propreté Conduites")
    proprete_camion = fields.Selection([('c', 'Conforme'), ('nc', 'Non Conforme')], string="Propreté Camion")

    remarque = fields.Text(string="Remarques")

    # Links to lab models
    reference_sample_ids = fields.One2many(
        'lab.sample.reference', 'checklist_id', string="Échantillon de Référence"
    )
    reception_sample_ids = fields.One2many(
        'lab.sample.reception', 'checklist_id', string="Échantillon Réception"
    )

    visa_responsable = fields.Char(string="Visa Responsable Contrôle Qualité")

    # Retour

    date_ret = fields.Date(string="Date de retour", default=fields.Date.context_today)
    client = fields.Char(string="Nom client")
    resp_acc = fields.Char(string="Resp acceptation")
    article = fields.Char(string="Désignation article")
    qty = fields.Integer(string="Quantité")
    lot = fields.Char(string="DF/ DLC/ LOT")

    storage = fields.Selection([
        ('conf', 'CONFORME'),
        ('nonconf', 'NON CONFORME'),
    ], string="Zone stockage")

    resp_treat = fields.Char(string="Resp traitement")

    # Isolation requirements
    iso_etiquette = fields.Boolean("Etiquette intacte")
    iso_capsule = fields.Boolean("Capsule intacte")
    iso_etui = fields.Boolean("Etui intact")
    iso_propre = fields.Boolean("Etat propre (pas trace huile/poussière)")
    iso_bosselure = fields.Boolean("Pas bosselure/rouille sur boites")
    iso_date = fields.Boolean("Date limite consommation valide")

    # Decision and destination
    dec_all_ok = fields.Boolean("Toutes exigences accomplies")
    dec_reten_return = fields.Boolean("Rétention et retour magasin échantillons")
    dec_sign = fields.Boolean("Signature magasinier acceptation")
    dec_else_isol = fields.Boolean("SINON isolement et destruction")

    # Destruction operation (minimized)
    destr_op = fields.Char("Nom opérateur")
    destr_step_c = fields.Boolean("Respect étapes destruction C")
    destr_step_nc = fields.Boolean("Respect étapes destruction NC")
    destr_sep_c = fields.Boolean("Respect principe séparation C")
    destr_sep_nc = fields.Boolean("Respect principe séparation NC")
    destr_hyg_c = fields.Boolean("Respect règles hygiène C")
    destr_hyg_nc = fields.Boolean("Respect règles hygiène NC")
    destr_tank_clean = fields.Boolean("État citerne propre")
    destr_tank_nc = fields.Boolean("État citerne NC")
    destr_tank_id_c = fields.Boolean("Id citerne C")
    destr_tank_id_nc = fields.Boolean("Id citerne NC")

    # Packaging treatment
    treat_destr = fields.Boolean("Destruction")
    treat_pack_type = fields.Char("Nature emballage")
    treat_disposal = fields.Char("Élimination benne déchets")

    treat_reuse_glass = fields.Boolean("Réutilisation verre")
    treat_wash_date = fields.Date("Date lavage")
    treat_wash_resp = fields.Char("Opérateur lavage")
    treat_prod_used = fields.Char("Produit utilisé")
    treat_bottles_clean = fields.Boolean("Bouteilles lavées propre")
    treat_bottles_nc = fields.Boolean("Bouteilles lavées NC")
    treat_prot_c = fields.Boolean("État protection C")
    treat_prot_nc = fields.Boolean("État protection NC")

    # Préforme
    uniformity_color = fields.Boolean('Uniformité de la couleur')
    grammage = fields.Boolean('Grammage')
    diametre = fields.Boolean('Diamètre')
    uniformite = fields.Boolean('Uniformité de goulot')

    # Poignée
    fixation_serrage = fields.Boolean('Fixation / Serrage')
    orientation_correcte = fields.Boolean('Orientation correcte')
    compatibilite_bouteille = fields.Boolean('Compatibilité avec la bouteille')

    # Bouchon
    bouchon_couleur = fields.Boolean('Couleur')
    compatibilite_bouchon = fields.Boolean('Compatibilité par rapport à la bouteille')
    fermeture = fields.Boolean('Fermeture')
    fissures = fields.Boolean('Fissures')




class LabSampleReference(models.Model):
    _name = 'lab.sample.reference'
    _description = 'Échantillon de Référence'

    checklist_id = fields.Many2one('quality.checklist.emballage', string="Checklist")
    reference_admin = fields.Char(string="N° Administratif")
    reference = fields.Char(string="Référence")
    acidite = fields.Float(string="Acidité")
    k232 = fields.Float(string="K232")
    k270 = fields.Float(string="K270")
    pesticides = fields.Float(string="Pesticides")
    degustation = fields.Text(string="Dégustation")


class LabSampleReception(models.Model):
    _name = 'lab.sample.reception'
    _description = 'Échantillon Réception'

    checklist_id = fields.Many2one('quality.checklist.emballage', string="Checklist")
    acidite = fields.Float(string="Acidité")
    k232 = fields.Float(string="K232")
    k270 = fields.Float(string="K270")
    pesticides = fields.Float(string="Pesticides")
    aspect = fields.Text(string="Aspect")
    degustation = fields.Text(string="Dégustation")