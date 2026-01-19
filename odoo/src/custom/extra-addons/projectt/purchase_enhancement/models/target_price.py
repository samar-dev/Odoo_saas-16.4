from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    max_purchase_price = fields.Float(
        string="Prix d'achat maximal",
        compute="_compute_prices",
        store=True,
        help="Coût d'achat maximal autorisé pour respecter le prix cible de vente.",
    )
    target_price = fields.Float(
        string="Prix cible",
        compute="_compute_prices",
        store=True,
        help="Prix de vente calculé à partir du coût total + marge bénéficiaire.",
    )
    is_target_price_valid = fields.Boolean(
        string="Prix cible valide",
        compute="_compute_prices",
        store=True,
        help="Indique si le prix de vente actuel respecte la fourchette entre le coût maximal et le prix cible.",
    )

    # Taux configurables
    profit_margin = 0.25  # marge de 25 %
    labor_rate = 3.5       # coût main-d'œuvre par heure
    overhead_rate = 8    # coût frais généraux par heure

    @api.depends('bom_ids.bom_line_ids', 'bom_ids.bom_line_ids.product_id.standard_price', 'list_price')
    def _compute_prices(self):
        """Calcule le prix cible et le coût d'achat maximum à partir de la nomenclature et de l'historique de production."""
        MrpProduction = self.env['mrp.production']

        for product in self:
            # 1️⃣ Récupération directe de la nomenclature (si existante)
            bom = product.bom_ids[:1]
            if not bom:
                product.target_price = 0.0
                product.max_purchase_price = 0.0
                product.is_target_price_valid = False
                continue

            # 2️⃣ Coût matière (optimisé via somme vectorisée)
            total_mat_cost = sum(
                line.product_qty * line.product_id.standard_price
                for line in bom.bom_line_ids
                if line.product_id
            )
            material_cost = total_mat_cost / bom.product_qty if bom.product_qty else 0.0

            # 3️⃣ Données de production groupées (évite boucle)
            productions = MrpProduction.search([('product_id.product_tmpl_id', '=', product.id)])
            if not productions:
                labor_cost = 0.0
                overhead_cost = 0.0
            else:
                total_duration = sum(productions.mapped('workorder_ids.duration'))
                total_qty = sum(productions.mapped('product_qty'))
                avg_duration = total_duration / total_qty if total_qty else 0.0

                # Conversion en heures
                labor_cost = avg_duration * (self.labor_rate / 60.0)
                overhead_cost = avg_duration * (self.overhead_rate / 60.0)

            # 4️⃣ Coût total et prix cible
            total_cost = material_cost + labor_cost + overhead_cost
            target_price = total_cost * (1 + self.profit_margin)
            product.target_price = target_price

            # 5️⃣ Calcul du coût d'achat maximal autorisé
            max_total_cost = product.list_price / (1 + self.profit_margin) if self.profit_margin else 0.0
            max_purchase_price = max_total_cost - labor_cost - overhead_cost
            product.max_purchase_price = max(max_purchase_price, 0.0)

            # 6️⃣ Vérification de cohérence du prix de vente
            product.is_target_price_valid = (
                product.list_price >= product.max_purchase_price
                and product.list_price <= product.target_price
            )


    @api.model
    def cron_compute_target_price_for_sale_products(self):
        sale_products = self.search([("sale_ok", "=", True)])
        sale_products._compute_prices()
