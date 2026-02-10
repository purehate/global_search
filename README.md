# Global Search for Odoo 17 Community

Spotlight-style global search for Odoo 17. Press **Ctrl+K** (or **Cmd+K** on Mac) to instantly search across models and jump to any record.

![Odoo 17](https://img.shields.io/badge/Odoo-17.0-blueviolet)
![License](https://img.shields.io/badge/License-MIT-green)

## Features

- **Keyboard shortcut** — `Ctrl+K` / `Cmd+K` opens the search from anywhere in Odoo
- **Spotlight-style overlay** — centered dialog with instant results, like macOS Spotlight or VS Code's Cmd+P
- **Multi-model search** — search Contacts, Sales Orders, Projects, Tasks, Invoices, CRM Leads from one place
- **Keyboard navigation** — Arrow keys to select, Enter to open, Escape to close
- **ORM only** — no raw SQL, fully respects Odoo record rules and access control
- **Configurable** — admins choose which models and fields are searchable
- **Fast** — 300ms debounce, limited results per model, indexed field searches

## Installation

1. Clone or download this repo into your Odoo 17 addons path
2. Restart Odoo
3. Go to **Apps** → Update Apps List
4. Search for "Global Search" and install

Default search configs are automatically created for installed modules (Contacts, Sales, Projects, Tasks, Invoices, CRM).

## Configuration

Go to **Settings → Technical → Global Search** to manage searchable models.

Each config entry has:

| Field | Description |
|-------|-------------|
| **Label** | Display name in results (e.g. "Contacts") |
| **Model** | Technical model name (e.g. `res.partner`) |
| **Search Fields** | Comma-separated fields to search (e.g. `name,email,phone`) |
| **Icon** | Font Awesome 4 icon class (e.g. `fa-address-book`) |
| **Limit** | Max results per model (default: 5) |
| **Sequence** | Display order |

## Usage

1. Press **Ctrl+K** (Windows/Linux) or **Cmd+K** (Mac), or click the search icon in the navbar
2. Type at least 2 characters
3. Results appear grouped by model
4. Use **Arrow keys** to navigate, **Enter** to open the record
5. Press **Escape** to close

## Architecture

```
global_search/
├── __manifest__.py                         # Module declaration (depends: web)
├── hooks.py                                # Post-install: creates default configs
├── models/
│   └── global_search_config.py             # Searchable model configuration
├── controllers/
│   └── main.py                             # /global_search/search JSON-RPC endpoint
├── security/
│   └── ir.model.access.csv                 # Read: all users, Write: admins
├── views/
│   └── global_search_config_views.xml      # Admin config UI
└── static/src/components/global_search/
    ├── global_search.js                    # OWL 2 systray + overlay component
    ├── global_search.xml                   # OWL template
    └── global_search.scss                  # Spotlight-style styling
```

### Design Principles

- **ORM only** — all searches use `Model.search(domain)`, never raw SQL
- **Security compliant** — searches run as the current user, respecting all record rules and ACLs
- **Graceful degradation** — models the user can't access are silently skipped
- **Validated config** — constraints ensure configured models and fields actually exist
- **OWL 2 / Odoo 17 native** — no legacy JavaScript, no jQuery

## Requirements

- Odoo 17 Community or Enterprise
- Python 3.10+
- No external dependencies beyond Odoo's `web` module

## License

MIT
