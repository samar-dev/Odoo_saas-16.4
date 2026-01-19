# Print Payment Methods

- Add the ability to print different reports from `account.payment` using a single
  button.

**Table of Contents**

- Features & Limitations
- Configuration
- Usage
- Dependencies

---

## Features

- A field has been introduced for `account.payment.method` called `is_printable`.
    - Using the following field will let odoo knows if the payment method has reports to
      print from the account payment.
- Two fields have been introduced for `account.payment.method.line`.
    - `qweb_template_id` for the qweb report view.
    - `report_paperformat_id` for the `paperformat_id` related to use.
- A new button called **Imprimer** has been introduced for `account.payment` form view.
    - Clicking the button will create the pdf file to print.
    - The report and paper format depends on the payment method.

---

## Configuration

1. Go to Accounting > Configuration > Payment Methods
2. Set `is_printable` to `True` for your payment method.
3. Accounting > Configuration > Journals
4. Select your journal and choose the desired payment method.
5. Set the qweb view and paper format for the payment method selected.

---

## Usage

1. Create a sale order/purchase order and validate it
2. Create the invoice/bill and validate it.
3. Register the payment and choose your payment method.
4. Go to the payment created.
5. A button called **Imprimer** appears in the header.
6. Click the button to get the report.

---

## Dependencies

### Odoo modules dependencies

| Module             | Why used?                                                  | Side effects |
|--------------------|------------------------------------------------------------|--------------|
| account            | needed to add the new introduced fields to payment methods |              |
| v__payment_methods | needed to inherit the `payment_method` tree view           |              |

### Python library dependencies

| Package | Why used? | URL doc |
|---------|-----------|---------|
