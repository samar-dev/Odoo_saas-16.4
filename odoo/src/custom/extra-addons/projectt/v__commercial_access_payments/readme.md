# Commercial Access Payments

**Table of Contents**

- Features & Limitations
- Configuration
- Usage
- Dependencies

---

## Features

- Add a new group called **Accès spécial au paiement** that gives access
  to `account_payment`, `account_payment_register`, `account_move`
  and `account_move_line`
- Access only for read, creat and edit, no deletion access
- Record rules to only see his payments, journal entry and journal items

---

## Configuration

1. Add the desired user to the group

---

## Usage

---

## Dependencies

### Odoo modules dependencies

| Module             | Why used?                                                                     | Side effects |
|--------------------|-------------------------------------------------------------------------------|--------------|
| account            | needed to access `account_move` and `account_payment` to inherit some methods |              |

### Python library dependencies

| Package | Why used? | URL doc |
|---------|-----------|---------|
