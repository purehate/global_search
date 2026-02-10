import logging

_logger = logging.getLogger(__name__)

# Default search configurations created on install.
# Only models that are actually installed will be configured.
_DEFAULT_CONFIGS = [
    ("Contacts", "res.partner", "name,email,phone", "fa-address-book", 10),
    ("Sales Orders", "sale.order", "name,client_order_ref", "fa-shopping-cart", 20),
    ("Projects", "project.project", "name", "fa-folder", 30),
    ("Tasks", "project.task", "name", "fa-tasks", 40),
    ("Invoices", "account.move", "name,ref", "fa-file-text", 50),
    ("CRM Leads", "crm.lead", "name,contact_name,email_from", "fa-filter", 60),
]


def _post_init_hook(env) -> None:
    """Create default global search configs for installed models."""
    Config = env["global.search.config"]
    for name, model_name, search_fields, icon, sequence in _DEFAULT_CONFIGS:
        if model_name not in env:
            continue
        # Only keep fields that actually exist on the model
        Model = env[model_name]
        valid_fields = [
            f.strip()
            for f in search_fields.split(",")
            if f.strip() and f.strip() in Model._fields
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
