from marshmallow import EXCLUDE, Schema, fields, validate


class OrderItemSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    listing_id = fields.Str(required=True)
    qty = fields.Int(required=True, validate=validate.Range(min=1))


class OrderCreateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    shop_id = fields.Str(required=True)
    items = fields.List(
        fields.Nested(OrderItemSchema), required=True, validate=validate.Length(min=1)
    )
    delivery_method = fields.Str(
        required=False, validate=validate.OneOf(["pickup", "delivery"]), load_default="pickup"
    )
    delivery_address = fields.Str(required=False, allow_none=True)
    delivery_lat = fields.Float(required=False, allow_none=True)
    delivery_lng = fields.Float(required=False, allow_none=True)
    payment_method = fields.Str(
        required=True, validate=validate.OneOf(["stripe", "flutterwave", "paystack", "cash"])
    )


class OrderSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Str(dump_only=True)
    buyer_id = fields.Str(dump_only=True)
    shop_id = fields.Str(dump_only=True)
    status = fields.Str(dump_only=True)
    total = fields.Int(dump_only=True)
    currency = fields.Str(dump_only=True)
    payment_method = fields.Str(dump_only=True)
    payment_status = fields.Str(dump_only=True)
    delivery_method = fields.Str(dump_only=True)
    delivery_address = fields.Str(dump_only=True)
    delivery_lat = fields.Float(dump_only=True)
    delivery_lng = fields.Float(dump_only=True)
    rider_id = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
