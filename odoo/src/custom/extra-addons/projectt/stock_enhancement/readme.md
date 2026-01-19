# Stock Enhancement


**Table of Contents**

- Features & Limitations
- Configuration
- Usage
- Dependencies

---

## Features

- Add two fields to the transfer form view : **Vehicle** and **Delivery person**
- Automatic generation of lot for items received without a lot

---

## Configuration

---

## Usage


---

## Dependencies

### Odoo modules dependencies

| Module        | Why used?                                                                   | Side effects |
|---------------|-----------------------------------------------------------------------------| ------------ |
| stock         | needed to add the new fields and methods to `stock_picking` model and views |              |
| fleet         | needed to access to `fleet_vehicle` model                                   |              |

### Python library dependencies

| Package | Why used? | URL doc |
| ------- | --------- | ------- |
