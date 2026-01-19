# MRP Product Line

This module allows to add the discount per line in the purchase orders

**Table of Contents**

- Features & Limitations
- Configuration
- Usage
- Dependencies

---

## Features

* Create a specific production line for a given product family, detailing its processes and components.
* When creating a bill of materials, you have the option to choose the product Line, and the system will generate the components and operations.
---

## Configuration

* To include an operation in the product list of a product Line, the operation must be a template (the 'template' checkbox is checked).

---

## Usage
* To access the product Lines :Manufacturing > Configuration > Product Lines
* To generate components and operations, simply select the product line in the bill of materials form.

---

## Dependencies

### Odoo modules dependencies

| Module               | Why used?                                                                              | Side effects |
|----------------------|----------------------------------------------------------------------------------------|--------------|
| mrp                  | access to the `mrp.bom`, `mrp.production`and `mrp.routing.workcenter` models and views |              |
| product              | access to the `product.template` views                                                 |              |
| quality              | access to groups                                                                       |              |
| quality_control      | access to menus and groups                                                             |              |
| mail                 | send mail notification                                                                 |              |
| v__message_service   | use  `_base_send_a_message` method                                                     |              |

### Python library dependencies

| Package  | Why used?                                         | URL doc                            |
|----------|---------------------------------------------------|------------------------------------|
