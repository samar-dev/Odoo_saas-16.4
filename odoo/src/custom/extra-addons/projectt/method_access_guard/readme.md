# Method Access Guard

**Table of Contents**

- Features & Limitations
- Configuration
- Usage
- Dependencies

---

## Features

- Add the ability to block certain methods from being executed.
- Methods will be blocked using groups and/or users.
- Application accessible for `base.group_system`

## Configuration

1. Go to Method Access Guard
2. Create your record by choosing the desired method name and model
3. Choose the groups and/or the users to block from executing the specified method.
4. Type a message to show to the end user.

---

## Usage

---

## Dependencies

### Odoo modules dependencies

| Module | Why used?                                          | Side effects |
|--------|----------------------------------------------------|--------------|
| web    | access to `_call_kw` method inside web controllers |              |

### Python library dependencies

| Package | Why used? | URL doc |
|---------|-----------|---------|

