# Communication Methods


**Table of Contents**

- Features & Limitations
- Configuration
- Usage
- Dependencies

---

## Features

Add 3 main methods to the `base` model

1) Create an activity and assign to a single `res.users` record
2) Send a chat message using channels, you have to pass `res.users` records and don't forget yourself :)
3) Send a notification to appear in the top right of the page

---

## Configuration

No configuration needed for this module

---

## Usage

1) self._base_create_activity()
2) self._base_send_a_message()
3) self._base_display_notification()

---

## Dependencies

### Odoo modules dependencies

| Module | Why used?                          | Side effects |
|--------|------------------------------------|--------------|
| mail   | needed to access the mail activity |              |

### Python library dependencies

| Package  | Why used?                                         | URL doc                            |
|----------|---------------------------------------------------|------------------------------------|
