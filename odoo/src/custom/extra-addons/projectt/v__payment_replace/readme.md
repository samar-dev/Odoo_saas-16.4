# Payment Replacement

- Add the possibility to set a payment as unpaid and replace it with another payment.

**Table of Contents**

- Features & Limitations
- Configuration
- Usage
- Dependencies

---

## Features

- Unpaid button will only be visible if `x_stage_id.type == 'must_be_sent`.
- Clicking Unpaid Button will set the payment as draft, cancel the payment and set `is_unpaid` to `True`.
- A ribbon will be visible in red if the payment is set as unpaid.
- Replace button will only be visible if `is_unpaid` is `True`.
- Replace button after replacing a payment will set the payment as replaced `is_replaced = True`.
- Replace button will be hidden if the total amount of the new payments equal the same amount of the original payment.
- A smart button has been added to the payment to show the new payments created.
- 2 filters has been added to the search view of `account_payment`, Unpaid filter and replaced filter.

---

## Configuration

No configuration is required.

---

## Usage

1. Register a new payment using one of the customized payment methods.
2. The customized payment must have a stage of type `must_be_sent`.
3. Reaching that stage Unpaid button will appear, click that button.
4. Replace button will appear to the ability to replace the payment.
5. After the payment being fully replaced the replace button will become invisible.

---

## Dependencies

### Odoo modules dependencies

| Module               | Why used?                                      | Side effects |
| -------------------- | ---------------------------------------------- | ------------ |
| account              | needed to set payment as unpaid and replace it |              |
| v\_\_payment_methods | needed to use the x_stage_id of the payment    |              |

### Python library dependencies

| Package | Why used? | URL doc |
| ------- | --------- | ------- |
