from marshmallow import Schema, fields, validate


class TodoSchema(Schema):
    id = fields.Integer(dump_only=True)
    title = fields.String(required=True, validate=validate.Length(max=200))
    description = fields.String(load_default="")
    completed = fields.Boolean(load_default=False)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
