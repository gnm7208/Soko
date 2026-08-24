from marshmallow import EXCLUDE, Schema, fields, validate


class PaymentIntentSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    order_id = fields.Str(required=True)
    provider = fields.Str(
        required=True, validate=validate.OneOf(["stripe", "flutterwave", "paystack"])
    )


class PaymentSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Str(dump_only=True)
    order_id = fields.Str(dump_only=True)
    provider = fields.Str(dump_only=True)
    provider_ref = fields.Str(dump_only=True)
    amount = fields.Int(dump_only=True)
    status = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
