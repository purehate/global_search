import logging
from typing import Any

from odoo import http
from odoo.exceptions import AccessError
from odoo.http import request

_logger = logging.getLogger(__name__)


class GlobalSearchController(http.Controller):
    """JSON-RPC controller for global search queries."""

    @http.route("/global_search/search", type="json", auth="user")
    def search(self, query: str = "", **kwargs: Any) -> list[dict]:
        """Search across all configured models for the given query.

        Uses the ORM (no raw SQL) and respects record rules / ACLs.

        Args:
            query: The search string (minimum 2 characters).

        Returns:
            List of result groups, each with model info and matching records.
        """
        if not query or len(query) < 2:
            return []

        configs = request.env["global.search.config"].sudo().search(
            [("active", "=", True)], order="sequence"
        )
        results: list[dict] = []

        for config in configs:
            model_name = config.model_name
            if model_name not in request.env:
                continue

            try:
                group = self._search_model(config, model_name, query)
                if group:
                    results.append(group)
            except AccessError:
                continue
            except ValueError as exc:
                _logger.warning(
                    "Global search config error on %s: %s", model_name, exc
                )
                continue

        return results

    def _search_model(
        self, config: Any, model_name: str, query: str
    ) -> dict | None:
        """Search a single model and return grouped results.

        Args:
            config: global.search.config record.
            model_name: Technical model name.
            query: The search string.

        Returns:
            Dict with model info and records, or None if no results.
        """
        Model = request.env[model_name]
        fields_list = [
            f.strip() for f in config.search_fields.split(",") if f.strip()
        ]
        if not fields_list:
            return None

        # Build OR domain: ['|', '|', (f1, ilike, q), (f2, ilike, q), (f3, ilike, q)]
        domain = [(f, "ilike", query) for f in fields_list]
        if len(domain) > 1:
            domain = ["|"] * (len(domain) - 1) + domain

        limit = config.limit or 5
        records = Model.search(domain, limit=limit)
        if not records:
            return None

        items = [{"id": rec.id, "name": rec.display_name} for rec in records]
        return {
            "model": model_name,
            "model_name": config.name,
            "icon": config.icon or "fa-file",
            "records": items,
        }
