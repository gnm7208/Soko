from marshmallow import EXCLUDE, Schema, fields, validate


class DisputeSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Str(dump_only=True)
    order_id = fields.Str(dump_only=True)
    raised_by = fields.Str(dump_only=True)
    reason = fields.Str(dump_only=True)
    status = fields.Str(dump_only=True)
    resolution_note = fields.Str(dump_only=True, allow_none=True)
    resolved_by = fields.Str(dump_only=True, allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class DisputeCreateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    order_id = fields.Str(required=True)
    reason = fields.Str(required=True, validate=validate.Length(min=5, max=2000))


class DisputeResolveSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    status = fields.Str(required=True, validate=validate.OneOf(["resolved", "rejected"]))
    resolution_note = fields.Str(required=False, allow_none=True)
