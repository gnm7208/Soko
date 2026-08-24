from marshmallow import EXCLUDE, Schema, fields, validate


class RegisterSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))
    full_name = fields.Str(required=True, validate=validate.Length(min=2, max=255))
    phone = fields.Str(required=False, allow_none=True)
    role = fields.Str(
        required=False, validate=validate.OneOf(["buyer", "retailer"]), load_default="buyer"
    )


class LoginSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    email = fields.Email(required=True)
    password = fields.Str(required=True)


class ProfileUpdateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    full_name = fields.Str(
        required=False, allow_none=True, validate=validate.Length(min=2, max=255)
    )
    phone = fields.Str(required=False, allow_none=True)


class UpgradeRetailerSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    shop_name = fields.Str(required=True, validate=validate.Length(min=2, max=255))
    category = fields.Str(required=True)
    address = fields.Str(required=True, allow_none=True)


class ProfileSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Str(dump_only=True)
    user_id = fields.Str(dump_only=True)
    role = fields.Str(dump_only=True)
    full_name = fields.Str(dump_only=True)
    phone = fields.Str(dump_only=True)
    avatar_url = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
