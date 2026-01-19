from . import models, wizards


def post_init_hook(env):
    stamp_name = "Timbre Fiscal"
    country_id = env.company.country_id
    tax_group_model = env["account.tax.group"]
    tax_model = env["account.tax"]
    product_template_model = env["product.template"]
    companies = env["res.company"].search([])
    for company in companies:
        # simulate the change of the company from the interface
        # each config created should belong to a single company
        env.company = company
        tax_group_id = tax_group_model.create(
            {"name": stamp_name, "country_id": country_id.id, "company_id": company.id}
        )
        product_template_id = product_template_model.create(
            {
                "name": stamp_name,
                "is_tax_stamp": True,
                "detailed_type": "service",
                "list_price": 0,
                # odoo wants if we don't have any company, the company_id should be False
                "company_id": company.id if len(companies) > 1 else None,
            }
        )
        for tax_type in ("sale", "purchase"):
            tax_id = tax_model.create(
                {
                    "name": stamp_name,
                    "amount_type": "fixed",
                    "active": True,
                    "type_tax_use": tax_type,
                    "amount": 1,
                    "tax_group_id": tax_group_id.id,
                    "country_id": country_id.id,
                    "company_id": company.id,
                }
            )
            if tax_type == "sale":
                product_template_id.taxes_id = tax_id
            elif tax_type == "purchase":
                product_template_id.supplier_taxes_id = tax_id
