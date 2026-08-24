from marshmallow import EXCLUDE, Schema, fields, validate


class SearchParamsSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    q = fields.Str(required=False, allow_none=True)
    category = fields.Str(required=False, allow_none=True)
    min_price = fields.Int(required=False, allow_none=True, validate=validate.Range(min=1))
    max_price = fields.Int(required=False, allow_none=True, validate=validate.Range(min=1))
    condition = fields.Str(
        required=False, validate=validate.OneOf(["new", "used"]), allow_none=True
    )
    lat = fields.Float(required=False, allow_none=True)
    lng = fields.Float(required=False, allow_none=True)
    radius = fields.Int(required=False, allow_none=True, validate=validate.Range(min=1))
    sort = fields.Str(
        required=False,
        validate=validate.OneOf(["price_asc", "price_desc", "newest", "popular"]),
        load_default="newest",
    )
    page = fields.Int(required=False, load_default=1, validate=validate.Range(min=1))
    per_page = fields.Int(required=False, load_default=20, validate=validate.Range(min=1, max=100))
