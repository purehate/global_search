# TrustedSec Odoo 17 Custom Addons

## Project Overview

This is a **custom addons directory** for an Odoo 17 Community instance deployed at `synergy.trustedsec.com`. It contains ~50 custom/OCA modules at the root level. This is NOT a full Odoo installation — just the addons.

## Key Conventions

### Module Structure
```
module_name/
├── __init__.py
├── __manifest__.py          # version: "17.0.x.x.x", license: "Other proprietary"
├── models/
├── controllers/
├── views/                   # XML view definitions
├── security/
│   └── ir.model.access.csv  # ACL matrix
├── data/                    # Initial data XML
├── static/src/
│   ├── components/          # OWL 2 components
│   └── scss/
├── report/
├── wizards/
└── tests/
```

### Python
- Odoo 17 uses Python 3.10+
- Models: `from odoo import api, fields, models`
- Use type hints on function signatures
- Docstrings on classes and public methods
- Specific exception handling (never bare `except:`)
- Files under 500 lines — split into modules if larger
- Field naming: `snake_case`
- Method naming: `_private_method()`, `action_public_method()`, `_compute_field()`

### JavaScript / Frontend
- **OWL 2** only — no legacy JS
- Files start with `/** @odoo-module */`
- Import from `@odoo/owl` and `@web/core/registry`
- Services via `useService()` from `@web/core/utils/hooks`
- Assets registered in `__manifest__.py` under `"web.assets_backend"`
- Glob patterns for asset bundles: `"module/static/src/components/**/*"`

### Manifest Pattern
```python
{
    "name": "Module Name",
    "version": "17.0.1.0.0",
    "author": "TrustedSec",
    "license": "Other proprietary",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/model_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "module/static/src/components/**/*",
        ],
    },
    "installable": True,
}
```

### Security CSV Format
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_model_user,model_user,model_model_name,base.group_user,1,0,0,0
access_model_admin,model_admin,model_model_name,base.group_system,1,1,1,1
```

### Views (XML Inheritance)
- Use `<xpath expr="..." position="after|before|inside|replace|attributes">`
- Menu items: `parent="base.menu_custom"` for Settings > Technical

## Coding Guidelines (User-Specified)

1. **NEVER** use bare `except:` — always specify exception types
2. **ALWAYS** add type hints to function signatures
3. **ALWAYS** add docstrings to classes and public functions
4. **NEVER** leave debug print statements
5. **NEVER** create files > 500 lines — split into modules
6. **NEVER** use `eval()`, `exec()`, or raw SQL with user input
7. **ALWAYS** validate and sanitize user input
8. **ALWAYS** use ORM — no raw SQL queries

## Active Custom Module: `global_search`

### What It Does
Spotlight-style global search for Odoo 17. Press **Ctrl+K / Cmd+K** to open a centered overlay that searches across configured models via ORM with keyboard navigation.

### File Map
```
global_search/
├── __init__.py                                    # imports controllers, models, hook
├── __manifest__.py                                # depends: web, post_init_hook
├── hooks.py                                       # _post_init_hook: creates default configs
├── models/
│   └── global_search_config.py                    # global.search.config model
├── controllers/
│   └── main.py                                    # /global_search/search JSON-RPC endpoint
├── security/
│   └── ir.model.access.csv                        # read=all users, write=admin
├── views/
│   └── global_search_config_views.xml             # tree/form views + Settings menu
└── static/src/components/global_search/
    ├── global_search.js                           # OWL 2 systray component + overlay
    ├── global_search.xml                          # OWL template
    └── global_search.scss                         # Spotlight-style overlay styling
```

### Architecture
- **Backend**: `global.search.config` model stores which models/fields to search. Controller builds OR domains and calls `Model.search()` per config. Respects ACLs (no sudo on search).
- **Frontend**: OWL 2 systray component. Registers global `keydown` listener for Ctrl+K/Cmd+K. Opens fixed-position overlay with debounced RPC search (300ms). Arrow key navigation + Enter to open record form view.
- **Install hook**: `_post_init_hook(env)` auto-creates configs for installed models (res.partner, sale.order, project.project, project.task, account.move, crm.lead). Validates fields exist before creating.
- **Config UI**: Settings > Technical > Global Search — admins add/remove/reorder searchable models and fields.

### Key Design Decisions
- ORM only, no raw SQL
- Search runs as current user (respects record rules)
- AccessError on any model is silently skipped
- Field/model validation via `@api.constrains`
- 300ms debounce on frontend to avoid excessive RPC calls
- Results limited per model (configurable, default 5)

## Existing Module Categories

| Category | Examples |
|----------|---------|
| Core TrustedSec | `trustedsec`, `trustedsec_base`, `trustedsec_hubspot`, `trustedsec_sow` |
| Mail/Communication | `mail_activity_board`, `mail_composer_cc_bcc`, `mail_quoted_reply` |
| Partner/Contact | `partner_firstname` (OCA), `partner_involvement`, `partner_affiliate` |
| CRM/Sales | `crm_involvement`, `crm_lead_partner_automatch`, `sale_restricted_qty` |
| Project | `project_involvement`, `project_department`, `project_parent`, `project_type` |
| OCA Utilities | `auditlog`, `base_user_role`, `server_action_mass_edit` |
| Debranding | `portal_odoo_debranding`, `website_odoo_debranding`, `server_depoweredby_*` |

## Git

- **Main branch**: `main`
- **Current branch**: `martin-search` (for global_search development)
- Commit format: `<type>(<scope>): <description>` — types: feat, fix, security, refactor, test, docs
