# Stock Enhancement


**Table of Contents**

- Features & Limitations
- Configuration
- Usage
- Dependencies

---

## Features

- In `purchase.order.line`, `product_packaging_id` takes by default the first value 
- In `purchase.order.line`, `product_packaging_qty` takes by default 1.0

---

## Dependencies

### Odoo modules dependencies

| Module   | Why used?                           | Side effects |
|----------|-------------------------------------| ------------ |
| purchase | Inherit `purchase.order.line` model |              |
