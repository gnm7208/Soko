from marshmallow import EXCLUDE, Schema, fields, validate


class PromotionSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Str(dump_only=True)
    shop_id = fields.Str(dump_only=True)
    listing_id = fields.Str(dump_only=True)
    discount_pct = fields.Int(dump_only=True, validate=validate.Range(min=1, max=99))
    starts_at = fields.DateTime(dump_only=True)
    ends_at = fields.DateTime(dump_only=True)
    active = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)


class PromotionCreateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    listing_id = fields.Str(required=True)
    discount_pct = fields.Int(required=True, validate=validate.Range(min=1, max=99))
    starts_at = fields.DateTime(required=True)
    ends_at = fields.DateTime(required=True)
