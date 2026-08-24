from marshmallow import EXCLUDE, Schema, fields, validate


class CategorySchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    slug = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    parent_id = fields.Str(required=False, allow_none=True)
    icon = fields.Str(required=False, allow_none=True)
    created_at = fields.DateTime(dump_only=True)
