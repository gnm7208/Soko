from marshmallow import EXCLUDE, Schema, fields, validate


class ShopSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Str(dump_only=True)
    owner_id = fields.Str(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=2, max=255))
    description = fields.Str(required=False, allow_none=True)
    logo_url = fields.Str(required=False, allow_none=True)
    cover_url = fields.Str(required=False, allow_none=True)
    category = fields.Str(required=True)
    address = fields.Str(required=False, allow_none=True)
    lat = fields.Float(required=False, allow_none=True)
    lng = fields.Float(required=False, allow_none=True)
    status = fields.Str(dump_only=True)
    rating_avg = fields.Float(dump_only=True)
    rating_count = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)


class ShopCreateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.Str(required=True, validate=validate.Length(min=2, max=255))
    description = fields.Str(required=False, allow_none=True)
    logo_url = fields.Str(required=False, allow_none=True)
    cover_url = fields.Str(required=False, allow_none=True)
    category = fields.Str(required=True)
    address = fields.Str(required=False, allow_none=True)
    lat = fields.Float(required=False, allow_none=True)
    lng = fields.Float(required=False, allow_none=True)
