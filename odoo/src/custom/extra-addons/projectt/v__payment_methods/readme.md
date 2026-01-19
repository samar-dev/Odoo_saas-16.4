# Payment Methods

- Installing the module will create 8 new payment methods in total, 4 inbound methods and 4 outbound

**Table of Contents**

- Features & Limitations
- Configuration
- Usage
- Dependencies

---

## Features

- Any payment has been registered from the wizard it won't be reconciled automatically if it has one of our payment methods.
- The new Payment methods has `stage_ids` so the user can create his own customized stages.
- Those stages will be added to the payment form view, in order to monitor the progress of our payment.
- One stage should have a `type = 'default'` in order to directly set it when the payment gets created.
- One stage should have a `type = 'reconcile'` in order to automatically reconcile the payment lines when we reach that stage.
- Payments methods will automatically be attached to your bank journal.
- If for some reason you didn't find them in your Bank Journal, Please add them manually.
- If no stage added to the customized payment method, you won't be able to process the payment.
- For any payment that is not reconciled and its type
  is `v-check` and `certified` we will check for the date of the payment if it passes 7 days compared to today we send a message to account group manager.
- Reset to draft button will be hidden if the payment gets cancelled.

---

## Configuration

1. Go to Accounting > Configuration > Payment Methods
2. Choose your payment method.
3. Set your customized stages.
4. Assure that you have one stage set as default.
5. Assure that you have only one stage that has `reconcile` = `True`.

For Payment to gets paid when you reconcile them set your outstanding account the same as the main account of your journal

---

## Usage

1. Create an invoice.
2. Put some products on it.
3. Confirm your invoice.
4. Register your payments, a wizard will be opened for you.
5. Select the new payment method and validate it.
6. Move from stage to stage using the new Button **Étape suivante**.
7. Once you reach your `reconcile` stage the payment will automatically gets reconciled.

---

## Dependencies

### Odoo modules dependencies

| Module  | Why used?                         | Side effects |
| ------- | --------------------------------- | ------------ |
| account | needed to add our payment_methods |              |

### Python library dependencies

| Package | Why used? | URL doc |
| ------- | --------- | ------- |
