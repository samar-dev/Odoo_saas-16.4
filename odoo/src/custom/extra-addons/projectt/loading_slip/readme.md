# Loading Slip

**Table of Contents**

- Features & Limitations
- Configuration
- Usage
- Dependencies

---

## Features

* This module adds a new report **Loading slip** in the area of accounting.
---

## Configuration

---

## Usage

*Go to Customers > Invoices > Print (tree view) > Loading slip


---

## Dependencies

### Odoo modules dependencies

| Module            | Why used?                                                                | Side effects |
|-------------------|--------------------------------------------------------------------------|--------------|
| account           | access to the `account.move`  model                                      |              |
| stock_enhancement | access to`vehicle_id` , `delivery_person_id` and `sum_net_weight` fields |              |

### Python library dependencies

| Package  | Why used?                                         | URL doc                            |
|----------|---------------------------------------------------|------------------------------------|
