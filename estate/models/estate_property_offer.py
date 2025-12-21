from odoo import api, fields, models

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer"

    price = fields.Float(string="Price", required=True)
    
    status = fields.Selection(
        [
            ("accepted", "Accepted"),
            ("refused", "Refused")
        ],
        string="Status",
        copy=False
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Partner Id",
        required=True,
    )

    property_id = fields.Many2one(
        "estate.property",
        string="Property",
        required=True,
    )

    validity = fields.Integer(default=7)
    date_deadline = fields.Date(
        compute="_compute_date_deadline",
        inverse="_inverse_date_deadline",
    )

    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        for record in self:
            create_dt = record.create_date or fields.Datetime.now()
            create_d = fields.Date.to_date(create_dt)
            record.date_deadline = fields.Date.add(create_d, days=record.validity or 0)

    def _inverse_date_deadline(self):
        for record in self:
            if not record.date_deadline:
                record.validity = 0
                continue
            create_dt = record.create_date or fields.Datetime.now()
            create_d = fields.Date.to_date(create_dt)
            record.validity = (record.date_deadline - create_d).days