# Payment Methods Tracking

Each time we move the payment from one stage to another,
a journal entry will be created and posted automatically to track the money

**Table of Contents**

- Features & Limitations
- Configuration
- Usage
- Dependencies

---

## Features

- Each stage of the `account_payment_method` will have a new field called `account_id`.
- The `account_id` is a required field.
- Moving from stage A to stage B will create a journal entry.
    - The account of the stage A will be credited.
    - The account of the stage B will be debited.

---

## Configuration

1. Go Accounting > Configuration > Payment Methods
2. Set the `account_id` of each stage

---

## Usage

1. Register a payment from the invoice/bill.
2. Moving the payment from stage to stage will create a journal entry.

---

## Dependencies

### Odoo modules dependencies

| Module               | Why used?                                        | Side effects |
|----------------------|--------------------------------------------------|--------------|
| v\_\_payment_methods | needed to access methods and views defined there |              |

### Python library dependencies

| Package | Why used? | URL doc |
|---------|-----------|---------|
