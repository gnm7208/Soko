from marshmallow import EXCLUDE, Schema, fields, validate


class ConversationSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Str(dump_only=True)
    shop_id = fields.Str(dump_only=True)
    buyer_id = fields.Str(dump_only=True)
    listing_id = fields.Str(dump_only=True, allow_none=True)
    last_message = fields.Str(dump_only=True)
    unread_count = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)


class MessageSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Str(dump_only=True)
    conversation_id = fields.Str(dump_only=True)
    sender_id = fields.Str(dump_only=True)
    body = fields.Str(dump_only=True)
    read = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)


class ConversationCreateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    shop_id = fields.Str(required=True)
    message = fields.Str(required=True, validate=validate.Length(min=1, max=2000))


class MessageCreateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    body = fields.Str(required=True, validate=validate.Length(min=1, max=2000))
