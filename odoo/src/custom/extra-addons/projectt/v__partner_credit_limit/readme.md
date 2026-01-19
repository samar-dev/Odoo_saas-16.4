# Partner Credit Limit

**Table of Contents**

- Features & Limitations
- Configuration
- Usage
- Dependencies

---

## Features

- Add the ability to set **credit limit** for customers.
- If the quotation order of the customer passed the amount specified, the order will not
  be validated
- The amount is depended on the company which means, the same customer can have
  multiple `x_credit_limit` depends on the company
- Also, you have the ability to set different `x_credit_limit` as default value
  depending on the company, also you can activate the blocking for company A and not for
  company B

---

## Configuration

1. Go to Settings > Sales > Invoicing Subtitle
2. Activate **Blocage par encours** and set the amount
3. You have the ability to set different amount per partner
4. Go To Sales > Orders > Customers
5. Choose your customer > Sales & Purchases page > **Plafond d'encours**
6. You must add yourself to the group **Modifier l'encours** in order to modify
   the `x_credit_limit` for the partner

---

## Usage

---

## Dependencies

### Odoo modules dependencies

| Module             | Why used?                                            | Side effects |
|--------------------|------------------------------------------------------|--------------|
| sale               | needed to access `sale_order` and configuration page |              |
| v__payment_replace | needed to access fields defined there                |              |

### Python library dependencies

| Package | Why used? | URL doc |
|---------|-----------|---------|
