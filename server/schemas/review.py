from marshmallow import EXCLUDE, Schema, fields, validate


class ReviewSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Str(dump_only=True)
    order_id = fields.Str(dump_only=True)
    reviewer_id = fields.Str(dump_only=True)
    shop_id = fields.Str(dump_only=True)
    rating = fields.Int(dump_only=True, validate=validate.Range(min=1, max=5))
    comment = fields.Str(dump_only=True, allow_none=True)
    created_at = fields.DateTime(dump_only=True)


class ReviewCreateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    order_id = fields.Str(required=True)
    rating = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    comment = fields.Str(required=False, allow_none=True, validate=validate.Length(max=2000))
