from odoo import api, fields, models
from odoo.exceptions import ValidationError


class GlobalSearchConfig(models.Model):
    """Configuration for global search: which models and fields to search."""

    _name = "global.search.config"
    _description = "Global Search Configuration"
    _order = "sequence, id"

    name = fields.Char(
        string="Label",
        required=True,
        help="Display name shown in search results (e.g. 'Contacts')",
    )
    model_name = fields.Char(
        string="Model",
        required=True,
        help="Technical model name, e.g. res.partner",
    )
    search_fields = fields.Char(
        string="Search Fields",
        required=True,
        help=(
            "Comma-separated field names to search, e.g. name,email,phone. "
            "Dotted relations are supported, e.g. partner_id.name"
        ),
    )
    icon = fields.Char(
        string="Icon",
        default="fa-file",
        help="Font Awesome 4 icon class, e.g. fa-address-book",
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    limit = fields.Integer(
        default=5,
        help="Maximum number of results returned per model",
    )

    @api.constrains("model_name")
    def _check_model_name(self) -> None:
        """Validate that the configured model exists in the registry."""
        for record in self:
            if record.model_name not in self.env:
                raise ValidationError(
                    "Model '%s' does not exist." % record.model_name
                )

    @api.constrains("search_fields", "model_name")
    def _check_search_fields(self) -> None:
        """Validate that all configured search fields exist on the model.

        Supports dotted paths like partner_id.name — validates each
        segment of the path by traversing the relational chain.
        """
        for record in self:
            if record.model_name not in self.env:
                continue
            for field_expr in record.search_fields.split(","):
                field_expr = field_expr.strip()
                if not field_expr:
                    continue
                self._validate_field_path(
                    record.model_name, field_expr
                )

    def _validate_field_path(self, model_name: str, field_path: str) -> None:
        """Walk a dotted field path and raise if any segment is invalid."""
        parts = field_path.split(".")
        current_model = self.env[model_name]
        for part in parts:
            if part not in current_model._fields:
                raise ValidationError(
                    "Field '%s' does not exist on model '%s'."
                    % (part, current_model._name)
                )
            field = current_model._fields[part]
            if hasattr(field, "comodel_name") and field.comodel_name:
                current_model = self.env[field.comodel_name]
