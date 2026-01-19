from odoo import models, fields, api


class StockVerification(models.Model):
    _name = "stock.verification"
    _description = "Stock Verification"

    product_id = fields.Many2one("product.product", string="Produit", required=True)
    date_from = fields.Datetime(string="Date à partir de", required=True)
    stock_initial = fields.Float(string="Stock Initial", default=0.0)

    total_entree = fields.Float(
        string="Total Entrée", compute="_compute_totals", store=True, digits=(10, 3)
    )
    total_livree = fields.Float(
        string="Total Livrée", compute="_compute_totals", store=True, digits=(10, 3)
    )
    total_utilise = fields.Float(
        string="Total Utilisé en Production",
        compute="_compute_totals",
        store=True,
        digits=(10, 3),
    )
    stock_declare = fields.Float(
        string="Stock Déclaré",
        compute="_compute_stock_declare",
        store=True,
        digits=(10, 3),
    )
    stock_logique = fields.Float(
        string="Stock Logique",
        compute="_compute_stock_logique",
        store=True,
        digits=(10, 3),
    )
    ecart = fields.Float(
        string="Écart", compute="_compute_stock_logique", store=True, digits=(10, 3)
    )
    coherence = fields.Selection(
        [("coherent", "Cohérent"), ("incoherent", "Incohérent")],
        string="Cohérence",
        compute="_compute_stock_logique",
        store=True,
        readonly=True,
    )
    diagnostic = fields.Text(
        string="Diagnostic", compute="_compute_stock_logique", store=True, readonly=True
    )

    @api.depends("product_id", "date_from")
    def _compute_totals(self):
        StockMove = self.env["stock.move"]

        for rec in self:
            if not rec.product_id or not rec.date_from:
                rec.total_entree = 0.0
                rec.total_livree = 0.0
                rec.total_utilise = 0.0
                continue

            moves = StockMove.search(
                [
                    ("product_id", "=", rec.product_id.id),
                    ("state", "=", "done"),
                    ("date", ">", rec.date_from),
                ]
            )

            rec.total_entree = sum(
                m.product_uom_qty
                for m in moves
                if m.location_id.usage not in ("internal", "transit")
                and m.location_dest_id.usage in ("internal", "transit")
            )

            rec.total_livree = sum(
                m.product_uom_qty
                for m in moves
                if m.location_id
                and m.location_id.usage in ("internal", "transit")
                and m.location_dest_id
                and m.location_dest_id.usage not in ("internal", "transit")
            )

            rec.total_utilise = sum(
                m.product_uom_qty
                for m in moves
                if m.picking_id
                and m.picking_id.name
                and m.picking_id.name.startswith("OF")
            )

    @api.depends("product_id")
    def _compute_stock_declare(self):
        StockQuant = self.env["stock.quant"]

        for rec in self:
            if not rec.product_id:
                rec.stock_declare = 0.0
                continue

            quants = StockQuant.search(
                [
                    ("product_id", "=", rec.product_id.id),
                    ("inventory_date", ">=", rec.date_from),
                    ("location_id.usage", "in", ["internal", "transit"]),
                ]
            )
            rec.stock_declare = sum(
                q.quantity - q.inventory_diff_quantity for q in quants
            )

    @api.depends(
        "stock_initial",
        "total_entree",
        "total_livree",
        "total_utilise",
        "stock_declare",
    )
    def _compute_stock_logique(self):
        for rec in self:
            sorties = rec.total_livree + rec.total_utilise
            rec.stock_logique = rec.stock_initial + rec.total_entree - sorties
            rec.ecart = rec.stock_declare - rec.stock_logique

            if abs(rec.ecart) < 1:
                rec.coherence = "coherent"
                rec.diagnostic = "Stock cohérent. Aucun écart significatif."
            else:
                rec.coherence = "incoherent"
                if rec.ecart > 0:
                    rec.diagnostic = (
                        "Le stock déclaré est SUPÉRIEUR au stock logique.\n"
                        "Possibles causes :\n"
                        "- Entrées manquantes\n"
                        "- Retours de production non comptés\n"
                        "- Mauvais stock initial\n"
                        f"Écart détecté : {rec.ecart:.2f} unités"
                    )
                else:
                    rec.diagnostic = (
                        "Le stock déclaré est INFÉRIEUR au stock logique.\n"
                        "Possibles causes :\n"
                        "- Sorties non enregistrées\n"
                        "- Perte, rebut ou erreur d’utilisation\n"
                        f"Écart détecté : {rec.ecart:.2f} unités"
                    )
