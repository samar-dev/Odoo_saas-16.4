# Block Unpaid Customers

**Table of Contents**

- Features & Limitations
- Configuration
- Usage
- Dependencies

---

## Features

- Add the ability to block customers, when a `sale_order` or `stock_picking` have that
  customer and the customer is blocked, you can't validate them
- If the quotation order of the customer passed the amount specified, the order will not
  be validated
- Inside the `res_partner` from view there is a new page that contains the history of
  blocking and unblocking the customer
- This module have only the possibility to block or unblock the customer manually
- Another modules can interact with this module to block or unblock the customer
  programmatically

---

## Configuration

1. Go to Settings > Sales > Invoicing Subtitle
2. Activate **Bloquer les clients impayés**

---

## Usage

1. Go the customer after activating the feature
2. Smart button available to toggle the customer blocking state
3. Toggle it and the history will be saved in **Historique de blocage/déblocage** page

---

## Dependencies

### Odoo modules dependencies

| Module | Why used?                                            | Side effects |
|--------|------------------------------------------------------|--------------|
| sale   | needed to access `sale_order` and configuration page |              |
| stock  | needed to inherit `stock_picking` methods            |              |

### Python library dependencies

| Package | Why used? | URL doc |
|---------|-----------|---------|
