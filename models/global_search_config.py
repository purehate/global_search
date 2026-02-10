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
        """Validate that the root of each search field exists on the model.

        For dotted paths like partner_id.name, only the first segment
        (partner_id) is validated. The ORM handles the rest at search time.
        """
        for record in self:
            if record.model_name not in self.env:
                continue
            Model = self.env[record.model_name]
            for field_expr in record.search_fields.split(","):
                field_expr = field_expr.strip()
                if not field_expr:
                    continue
                # Only validate the root field — dotted paths are
                # resolved by the ORM at search time
                root_field = field_expr.split(".")[0]
                if root_field not in Model._fields:
                    raise ValidationError(
                        "Field '%s' does not exist on model '%s'."
                        % (root_field, record.model_name)
                    )
