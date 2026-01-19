# Data Access Guard

**Table of Contents**

- Features & Limitations
- Configuration
- Usage
- Dependencies

---

## Features

- Add the ability to hide certain records from being displayed.
- Application accessible for `base.group_system`
- Work only for front not for backend
- It won't add access if the user already has no access to that record

## Configuration

1. Go to Data Access Guard
2. Create your record by choosing the desired model
3. Choose the groups and/or the users to apply the domain for them.
4. Choose your domain, for current user you can use `user`

---

## Usage

---

## Dependencies

### Odoo modules dependencies

| Module | Why used?                                                         | Side effects |
|--------|-------------------------------------------------------------------|--------------|
| web    | access to `_call_kw`, `search_read` method inside web controllers |              |

### Python library dependencies

| Package | Why used? | URL doc |
|---------|-----------|---------|

