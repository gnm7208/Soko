from marshmallow import EXCLUDE, Schema, fields, validate


class ListingSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Str(dump_only=True)
    shop_id = fields.Str(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=2, max=255))
    description = fields.Str(required=False, allow_none=True)
    price = fields.Int(required=True, validate=validate.Range(min=1))
    currency = fields.Str(dump_only=True)
    category_id = fields.Str(required=False, allow_none=True)
    condition = fields.Str(
        required=False, validate=validate.OneOf(["new", "used"]), load_default="new"
    )
    stock = fields.Int(required=False, validate=validate.Range(min=0), load_default=1)
    status = fields.Str(dump_only=True)
    location = fields.Str(dump_only=True)
    lat = fields.Float(dump_only=True)
    lng = fields.Float(dump_only=True)
    image_url = fields.Method("get_image_url", dump_only=True)
    created_at = fields.DateTime(dump_only=True)

    def get_image_url(self, obj):
        return obj.images[0].url if obj.images else None


class ListingCreateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    title = fields.Str(required=True, validate=validate.Length(min=2, max=255))
    description = fields.Str(required=False, allow_none=True)
    price = fields.Int(required=True, validate=validate.Range(min=1))
    category_id = fields.Str(required=False, allow_none=True)
    condition = fields.Str(
        required=False, validate=validate.OneOf(["new", "used"]), load_default="new"
    )
    stock = fields.Int(required=False, validate=validate.Range(min=0), load_default=1)


class ListingImageSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Str(dump_only=True)
    url = fields.Str(dump_only=True)
    position = fields.Int(dump_only=True)
