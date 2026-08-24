from marshmallow import EXCLUDE, Schema, fields, validate


class NotificationSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Str(dump_only=True)
    user_id = fields.Str(dump_only=True)
    type = fields.Str(
        dump_only=True, validate=validate.OneOf(["order", "message", "promotion", "system"])
    )
    title = fields.Str(dump_only=True)
    body = fields.Str(dump_only=True, allow_none=True)
    read = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)


class NotificationMarkReadSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    notification_id = fields.Str(required=True)
