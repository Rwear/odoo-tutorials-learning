from odoo import api,fields, models

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

    state = fields.Selection(
        [
            ("new", "New"),
            ("offer_received", "Offer Received"),
            ("offer_accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("cancelled", "Cancelled"),
        ],
        string="State",
        required=True,
        copy=False,
        default="new"
        
    )

    active = fields.Boolean(default=True)

    _check_expected_price = models.Constraint(
        "CHECK(expected_price > 0)",
        "Expected price must be strictly positive.",
    )

    property_type_id = fields.Many2one("estate.property.type", string="Property Type")

    # Buyer(partner) and Salesperson(user)
    buyer_id = fields.Many2one(
        "res.partner",
        string="Buyer",
        copy=False,
    )

    salesperson_id = fields.Many2one(
        "res.users",
        string="Salesperson",
        default=lambda self: self.env.user,
    )

    tag_ids = fields.Many2many(
        "estate.property.tag",
        string="Tags",
    )

    offer_ids = fields.One2many(
        "estate.property.offer",
        "property_id",
        string="Offers"
    )
    
    total_area = fields.Float(required=False, compute="_compute_total_area")

    
    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = (record.living_area or 0) + (record.garden_area or 0)


    best_price = fields.Float(compute="_compute_best_price")

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            prices = record.offer_ids.mapped("price")
            record.best_price = max(prices) if prices else 0
    
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(
        compute="_compute_date_deadline",
        inverse="_inverse_date_deadline"
    )

    @api.depends("date_availability", "validity")
    def _compute_date_deadline(self):
        for record in self:
            create_dt = record.create_date or fields. Datetime.now()
            create_d = fields.Date.to_date(create_dt)
            record.date_deadline = fields.Date.add(create_d, days=record.validity or 0)
    
    def _inverse_date_deadline(self):
        for record in self:
            if not record.date_deadline:
                continue
            create_dt = record.create_date or fields.Datetime.now()
            create_d = fields.Date.to_date(create_dt)
            record.validity = (record.date_deadline - create_d).days