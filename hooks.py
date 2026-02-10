import logging
from typing import Any

_logger = logging.getLogger(__name__)

# Default search configurations created on install/upgrade.
# Only models that are actually installed will be configured.
_DEFAULT_CONFIGS = [
    ("Contacts", "res.partner", "name,email,phone", "fa-address-book", 10),
    ("Sales / Quotations", "sale.order", "name,client_order_ref,partner_id.name", "fa-shopping-cart", 20),
    ("Projects", "project.project", "name,partner_id.name", "fa-folder", 30),
    ("Tasks", "project.task", "name", "fa-tasks", 40),
    ("Invoices", "account.move", "name,ref,partner_id.name", "fa-file-text", 50),
    ("CRM Leads", "crm.lead", "name,contact_name,email_from,partner_name", "fa-filter", 60),
]


def _field_path_exists(env, model: Any, field_path: str) -> bool:
    """Check if a dotted field path (e.g. partner_id.name) is valid."""
    parts = field_path.split(".")
    current = model
    for part in parts:
        if part not in current._fields:
            return False
        field = current._fields[part]
        if hasattr(field, "comodel_name") and field.comodel_name:
            current = env[field.comodel_name]
    return True


def _post_init_hook(env) -> None:
    """Create default global search configs for installed models."""
    _ensure_default_configs(env)


def _ensure_default_configs(env) -> None:
    """Create missing default configs. Safe to call multiple times."""
    Config = env["global.search.config"]
    existing = Config.search([]).mapped("model_name")

    for name, model_name, search_fields, icon, sequence in _DEFAULT_CONFIGS:
        if model_name not in env:
            continue
        # Skip duplicate model entries (e.g. sale.order for both Orders and Quotations)
        # but allow if the label is different
        existing_for_name = Config.search([
            ("model_name", "=", model_name),
            ("name", "=", name),
        ])
        if existing_for_name:
            continue

        Model = env[model_name]
        valid_fields = [
            f.strip()
            for f in search_fields.split(",")
            if f.strip() and _field_path_exists(env, Model, f.strip())
        ]
        if not valid_fields:
            continue
        Config.create(
            {
                "name": name,
                "model_name": model_name,
                "search_fields": ",".join(valid_fields),
                "icon": icon,
                "sequence": sequence,
            }
        )
        _logger.info("Global search: configured %s (%s)", name, model_name)
