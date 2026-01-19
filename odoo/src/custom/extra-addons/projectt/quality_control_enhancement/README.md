# Quality enhancement

This module add some functionality to the quality module.

**Table of Contents**

- Features & Limitations
- Configuration
- Usage
- Dependencies

---

## Features

- Add some count check (Success checks, Validated checks, Failed checks) to quality dashboard(kanban view).
- Quality Check: Add new state **validate by RMQ** to quality check form.
- Quality Check: Add filter **validate by RMQ**.
- Quality Alert: Add a domain to display only the items that exist in the transfer.

---

## Configuration

---

## Usage

---

## Dependencies

### Odoo modules dependencies

| Module              | Why used?                                                                          | Side effects |
|---------------------|------------------------------------------------------------------------------------|--------------|
| quality_control     | access to the `quality.alert`,`quality.alert.team`,`quality.check` model and views |              |

### Python library dependencies

| Package  | Why used?                                         | URL doc                            |
|----------|---------------------------------------------------|------------------------------------|
