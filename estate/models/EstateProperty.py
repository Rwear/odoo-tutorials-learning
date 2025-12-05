from odoo import fields, models

class EstateProperty(models.Model):
    """Real Estate Property (tutorial exercise)."""
    _name = "estate.property"
    _description = "Estate Property"

    title = fields.Char(required = True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(
        string="Available Date",
        copy=False,
        default= lambda self: fields.Date.add(fields.Date.today(), months=3)
    )
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(
        string="Selling Price",
        readonly=True,
        copy=False
    )
    bedrooms = fields.Integer(
        string="Bedrooms",
        default=2
    )
    living_area = fields.Integer("Living Area (sqm)")
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()

    garden_orientation = fields.Selection(
        [
            ("north", "North"),
            ("south", "South"),
            ("east", "East"),
            ("west", "West")
        ],
        string="Garden Orientation"
    )

    status = fields.Selection([
        ("new", "New"),
        ("offer_received", "Offer Received"),
        ("offer_accepted", "Offer Accepted"),
        ("sold", "Sold"),
        ("canceled", "Canceled")
    ])

    active = fields.Boolean(default=True)

    _expected_price_check = models.Constraint(
        "CHECK (expected_price > 0)",
        "Expected price must be positive"
    )

   
    
