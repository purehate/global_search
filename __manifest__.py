{
    "name": "Global Search",
    "version": "17.0.1.1.0",
    "summary": "Spotlight-style search across models (Cmd+K / Ctrl+K)",
    "description": (
        "Adds a Spotlight-style global search to Odoo. "
        "Press Cmd+K (Mac) or Ctrl+K to open a floating search dialog "
        "that searches across configured models using the ORM. "
        "Results are grouped by model with keyboard navigation."
    ),
    "author": "TrustedSec",
    "license": "MIT",
    "depends": ["web"],
    "data": [
        "security/ir.model.access.csv",
        "views/global_search_config_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "global_search/static/src/components/**/*",
        ],
    },
    "post_init_hook": "_post_init_hook",
    "installable": True,
    "auto_install": False,
}
