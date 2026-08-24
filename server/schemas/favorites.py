from marshmallow import EXCLUDE, Schema, fields


class FavoriteSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Str(dump_only=True)
    user_id = fields.Str(dump_only=True)
    listing_id = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)


class FavoriteCreateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    listing_id = fields.Str(required=True)
