# Production Date

- This module allows the addition of production dates to products that are tracked by serial number or lots during production.

**Table of Contents**

- Features & Limitations
- Configuration
- Usage
- Dependencies

---

## Features


- Add production dates to products lots that are tracked by serial number or lots during production.

---

## Configuration

1. Go to Inventory - Configuration then Activate "Production Dates"
2. Go to the desired product, then "Inventory" page and activate "Production Date"
3. Assure that you save the changes.

---

## Usage

- In Production, when you add the stock lot, the production date is added in the "Dates" page

---

## Dependencies

### Odoo modules dependencies

| Module            | Why used?                   | Side effects |
|-------------------|-----------------------------| ------------ |
| stock             | needed to add the features  |              |
| product_expiry    | needed to add the features  |              |

### Python library dependencies

| Package | Why used? | URL doc |
| ------- | --------- | ------- |
