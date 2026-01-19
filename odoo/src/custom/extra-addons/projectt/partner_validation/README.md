# Partner Validation

This module supports a contact validation process.

**Table of Contents**

- Features & Limitations
- Configuration
- Usage
- Dependencies

---

## Features

- Users can submit customer/vendor creation requests.
- Admins(sale/purchase) can define the validators of the request.
- Validators can review and approve product customer/vendor creation requests.
- Once approved, new customer/vendor are available throughout the system, otherwise this customer/supplier remains archived and not available in the system.

---

## Configuration

---

## Usage

---

## Dependencies

### Odoo modules dependencies

| Module             | Why used?                           | Side effects |
|--------------------|-------------------------------------|--------------|
| account            | access to the `res.partner` views   |              |
| sale               | access to groups                    |              |
| purchase           | access to groups                    |              |
| v__message_service | use  `_base_create_activity` method |              |

### Python library dependencies

| Package  | Why used?                                         | URL doc                            |
|----------|---------------------------------------------------|------------------------------------|
