from marshmallow import EXCLUDE, Schema, fields, validate


class WalletSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Str(dump_only=True)
    user_id = fields.Str(dump_only=True)
    balance = fields.Int(dump_only=True)
    currency = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)


class WalletTransactionSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Str(dump_only=True)
    wallet_id = fields.Str(dump_only=True)
    type = fields.Str(dump_only=True, validate=validate.OneOf(["credit", "debit"]))
    amount = fields.Int(dump_only=True)
    ref = fields.Str(dump_only=True, allow_none=True)
    description = fields.Str(dump_only=True, allow_none=True)
    created_at = fields.DateTime(dump_only=True)


class PayoutRequestSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Str(dump_only=True)
    wallet_id = fields.Str(dump_only=True)
    amount = fields.Int(dump_only=True, validate=validate.Range(min=1))
    status = fields.Str(dump_only=True)
    note = fields.Str(dump_only=True, allow_none=True)
    created_at = fields.DateTime(dump_only=True)


class PayoutCreateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    amount = fields.Int(required=True, validate=validate.Range(min=1))
    note = fields.Str(required=False, allow_none=True)
