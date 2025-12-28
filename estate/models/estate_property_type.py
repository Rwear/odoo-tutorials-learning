from odoo import fields, models

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate Property Type"

    name = fields.Char(string="Property Type", required=True)
    
    _check_name_unique = models.Constraint(
        "UNIQUE(name)",
        "Property type name must be unique.",
    )