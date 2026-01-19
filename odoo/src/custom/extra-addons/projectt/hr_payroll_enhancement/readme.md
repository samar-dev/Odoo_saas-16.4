# Stock Credit Note

Generate credit note from transfer

**Table of Contents**

- Features & Limitations
- Configuration
- Usage
- Dependencies

---

## Features

- If **Create credit note** checked, a credit note can be generated from current **transfer**.
- If the transfer is linked to an accounted invoice, a credit note for that invoice will be generated when clicking the **Credit note** button 
- If not, upon the **validation** of the transfer, a credit note will be **automatically generated** directly from this transfer (without any connection to an invoice).

---

## Configuration
1. Inventory > Configuration > Operations Types > Form view > Other > **Create credit note**

---

## Usage


---

## Dependencies

### Odoo modules dependencies

| Module              | Why used?                                                                                    | Side effects |
|---------------------|----------------------------------------------------------------------------------------------| ------------ |
| stock               | needed to add the new fields and methods to `stock_picking` and  `stock_picking_type` models |              |
| account             | needed to access to `account_move` model                                                     |              |
| sale_stock          | needed to use the `sale_id` and `sale_line_id` fields                                        |              |
| stock_picking_batch | needed to inherit `view_picking_type_form_inherit` view                                      |              |

### Python library dependencies

| Package | Why used? | URL doc |
| ------- | --------- | ------- |
