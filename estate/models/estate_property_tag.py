from odoo import fields, models

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Estate Property Tag"

    name = fields.Char(string="Tag Name", required=True)

    _check_name_unique = models.Constraint(
        "UNIQUE(name)",
        "Property tag name must be unique.",
    )
    