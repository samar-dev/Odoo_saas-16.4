# Tax Stamp

- Installing module will create a `product_template`, `account_tax` and `account_tax_group`.
- `product_template` created will be called **Timbre Fiscal** and have the following attribute `is_tax_stamp` equal to `True`.
- New field called `is_taxable` is available for `res_partner`.

**Table of Contents**

- Features & Limitations
- Configuration
- Usage
- Dependencies

---

## Features

- If the `account_move` created has a taxable partner and the currency is TND and is not partially refuneded, the tax stamp is mandatory and can't be deleted or modified manually.
- Changing the `account_move` that make the above condition as `False` the tax stamp line will removed automatically.
- If the `account_move.is_partial_refund` equals to `True` you can delete the tax stamp manually.
- The value of the tax stamp is controlled from the `account_tax`.
- The Product must have a price of zero always.

---

## Configuration

1. Go to the tax stamp product **Timbre Fiscal** and add the income and the expense account.

---

## Usage

1. Work as you usual nothing will be changed.
2. Any invoice gets created the tax stamp will be added automatically.

---

## Dependencies

### Odoo modules dependencies

| Module             | Why used?                                        | Side effects |
|--------------------|--------------------------------------------------| ------------ |
| account            | needed to add the tax stamp to account_move_line |              |
| account_accountant | needed to configure the accounts for the product |              |
| product            | needed to add the tax stamp as a product         |              |

### Python library dependencies

| Package | Why used? | URL doc |
| ------- | --------- | ------- |
