from marshmallow import EXCLUDE, Schema, fields, validate


class DeliverySchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Str(dump_only=True)
    order_id = fields.Str(dump_only=True)
    rider_id = fields.Str(dump_only=True)
    status = fields.Str(
        dump_only=True,
        validate=validate.OneOf(
            ["pending", "assigned", "picked_up", "in_transit", "delivered", "cancelled"]
        ),
    )
    method = fields.Str(dump_only=True)
    address = fields.Str(dump_only=True, allow_none=True)
    lat = fields.Float(dump_only=True, allow_none=True)
    lng = fields.Float(dump_only=True, allow_none=True)
    eta = fields.DateTime(dump_only=True, allow_none=True)
    created_at = fields.DateTime(dump_only=True)


class DeliveryUpdateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    status = fields.Str(
        required=True,
        validate=validate.OneOf(["assigned", "picked_up", "in_transit", "delivered", "cancelled"]),
    )


class TrackingUpdateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    lat = fields.Float(required=True)
    lng = fields.Float(required=True)
    status = fields.Str(
        required=False,
        validate=validate.OneOf(["picked_up", "in_transit", "delivered"]),
        load_default="in_transit",
    )
