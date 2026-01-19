# Payment Methods

**Table of Contents**

- Features & Limitations
- Configuration
- Usage
- Dependencies

---

## Features

- You can use a single journal with the `withholding_tax` records but using different
  accounts
- You have a withholding tax for sales and purchases
- The `subtract_tax_stamp` feature will work only if the module `v__tax_stamp` is
  installed

---

## Configuration

1. Go to Accounting > Configuration > **Retenue à la source**
2. Choose the appropriate name for your record.
3. Select if it is applicable for sales or purchases.
4. Select the journal will be used when the payment gets created
5. Select the account that will be used in place of `default_account_id` of the journal

---

## Usage

1. Create an invoice/bill.
2. Register your payment after validating the invoice/bill.
3. Check **Avec Retenue** checkbox and choose the withholding record template you create

---

## Dependencies

### Odoo modules dependencies

| Module             | Why used?                                    | Side effects |
|--------------------|----------------------------------------------|--------------|
| account            | needed to add our taxes                      |              |
| v__payment_methods | needed to inherit a method was defined there |              |

### Python library dependencies

| Package | Why used? | URL doc |
|---------|-----------|---------|
