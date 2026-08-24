from marshmallow import EXCLUDE, Schema, fields, validate


class ShopApprovalSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    shop_id = fields.Str(required=True)
    status = fields.Str(required=True, validate=validate.OneOf(["approved", "rejected"]))
    note = fields.Str(required=False, allow_none=True)


class MetricsSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    total_orders = fields.Int(dump_only=True)
    total_revenue = fields.Int(dump_only=True)
    total_shops = fields.Int(dump_only=True)
    total_users = fields.Int(dump_only=True)
    total_listings = fields.Int(dump_only=True)
    period = fields.Str(dump_only=True, allow_none=True)
