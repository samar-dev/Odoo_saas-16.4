# Purchase Discount

This module allows to add the discount per line in the purchase orders

**Table of Contents**

- Features & Limitations
- Configuration
- Usage
- Dependencies

---

## Features

* You can add a discount in the purchase order line.
* In a multi-company context, the quote generated from a price request includes the discount mentioned in the request.
---

## Configuration

---

## Usage

---

## Dependencies

### Odoo modules dependencies

| Module                            | Why used?                                                                | Side effects |
|-----------------------------------|--------------------------------------------------------------------------|--------------|
| purchase                          | access to the `purchase.order` and `purchase.order.line`  model and views |              |
| account                           | inherit `_convert_to_tax_base_line_dict` method                          |              |
| sale_purchase_inter_company_rules | inherit `_prepare_sale_order_line_data` method                           |              |

### Python library dependencies

| Package  | Why used?                                         | URL doc                            |
|----------|---------------------------------------------------|------------------------------------|
