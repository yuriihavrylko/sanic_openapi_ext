import pytest
from marshmallow import Schema, fields
from sanic_ext.extensions.openapi.definitions import Parameter
from sanic_ext.extensions.openapi import types as doc

from sanic_openapi_ext.marshmallow import open_api_schemas, open_api_schemas_params


def test_open_api_schemas_with_empty_schema():
    class EmptySchema(Schema):
        pass

    result = open_api_schemas(EmptySchema())
    assert result == {}


def test_open_api_schemas_with_unsupported_field():
    class UnsupportedFieldSchema(Schema):
        custom_field = fields.Field()

    result = open_api_schemas(UnsupportedFieldSchema())
    assert isinstance(result["custom_field"], doc.String)


def test_open_api_schemas_with_nested_schema_passed_as_json_and_many():
    class SimpleSchema(Schema):
        id = fields.Int(required=True, allow_none=False)
        step_no = fields.Int(required=True, allow_none=False)

    result = open_api_schemas(SimpleSchema(), is_json=True, many=True)
    assert isinstance(result, doc.Array)
    assert "id" in result.fields["items"].fields["properties"]
    assert "step_no" in result.fields["items"].fields["properties"]


def test_open_api_schemas_params_with_empty_schema():
    class EmptySchema(Schema):
        pass

    result = open_api_schemas_params(EmptySchema())
    assert result == []


def test_open_api_schemas_params_with_unsupported_field():
    class UnsupportedFieldSchema(Schema):
        custom_field = fields.Field()

    result = open_api_schemas_params(UnsupportedFieldSchema())
    assert result[0].fields["name"] == "custom_field"
    assert isinstance(result[0].fields["schema"], doc.String)


def test_uncovered_schema_to_openapi_mapping():
    class UncoveredSchema(Schema):
        decimal_field = fields.Decimal()
        bool_field = fields.Bool()

    result = open_api_schemas(UncoveredSchema())
    assert isinstance(result["decimal_field"], doc.String)
    assert isinstance(result["bool_field"], doc.Boolean)


def test_open_api_schemas_params_with_date_field():
    class DateFieldSchema(Schema):
        date = fields.Date()

    result = open_api_schemas_params(DateFieldSchema())
    assert isinstance(result[0], Parameter)
    assert result[0].fields["name"] == "date"
    assert isinstance(result[0].fields["schema"], doc.Date)


@pytest.mark.parametrize(
    "marshmallow_type, openapi_type",
    [
        (fields.Int, doc.Integer),
        (fields.Integer, doc.Integer),
        (fields.Str, doc.String),
        (fields.String, doc.String),
        (fields.Boolean, doc.Boolean),
        (fields.Float, doc.Float),
        (fields.DateTime, doc.DateTime),
        (fields.Date, doc.Date),
        (fields.Time, doc.Time),
    ],
)
def test_simple_types(marshmallow_type, openapi_type):
    schema = Schema.from_dict({"value": marshmallow_type()})()

    result = open_api_schemas(schema)
    assert isinstance(result["value"], openapi_type)


@pytest.mark.parametrize(
    "marshmallow_type, openapi_type, inner_type, inner_field",
    [
        (fields.List, doc.Array, fields.Int, doc.Integer),
        (fields.List, doc.Array, fields.Str, doc.String),
        (fields.List, doc.Array, fields.Float, doc.Float),
        (fields.List, doc.Array, fields.Boolean, doc.Boolean),
    ],
)
def test_complex_types(marshmallow_type, openapi_type, inner_type, inner_field):
    schema = Schema.from_dict({"value": marshmallow_type(inner_type())})()

    result = open_api_schemas(schema)
    assert isinstance(result["value"], openapi_type)
    assert isinstance(result["value"].fields["items"], inner_field)


@pytest.mark.parametrize(
    "marshmallow_type, openapi_type",
    [
        (fields.Nested, doc.Object),
    ],
)
def test_nested_types(marshmallow_type, openapi_type):
    class SimpleSchema(Schema):
        id = fields.Int(required=True, allow_none=False)
        step_no = fields.Int(required=True, allow_none=False)

    schema = Schema.from_dict({"value": marshmallow_type(SimpleSchema)})()
    result = open_api_schemas(schema)
    assert isinstance(result["value"], openapi_type)
