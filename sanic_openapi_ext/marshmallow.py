from marshmallow import fields, Schema
from sanic_ext.extensions.openapi import types as doc
from sanic_ext.extensions.openapi.definitions import Parameter
from typing import List

# Mapping between Marshmallow fields and OpenAPI fields
MAP_MARSHMALLOW_IN_OPEN_API = {
    # Dates
    fields.DateTime: doc.DateTime,
    fields.Date: doc.Date,
    fields.Time: doc.Time,
    # Numbers
    fields.Integer: doc.Integer,
    fields.Int: doc.Integer,
    fields.Float: doc.Float,
    fields.Decimal: doc.String,
    # Base types
    fields.String: doc.String,
    fields.Str: doc.String,
    fields.Boolean: doc.Boolean,
    fields.Bool: doc.Boolean,
    # Complex types
    fields.Enum: doc.Schema,
    fields.List: doc.Array,
    fields.Nested: doc.Object,
}


def open_api_schemas(
    schema: Schema, is_json: bool = False, many: bool = False
) -> doc.Schema:
    """
    Generate swagger documentation from a Marshmallow schema.

    Args:
        schema (Schema): The marshmallow schema object.
        is_json (bool, optional): If true, returns a doc.JsonBody. Default is False.
        many (bool, optional): If true, returns a doc.List. Default is False.

    Returns:
        doc.Schema: The swagger documentation schema.
    """

    swagger_schema = {}

    # Generating swagger schema for each field in the marshmallow schema
    for field_name in schema.fields:
        field_schema = schema.fields[field_name]
        swagger_schema[field_name] = marshmallow_to_openapi(field_name, field_schema)

    if schema.many is True or many:
        return doc.Array(swagger_schema)
    if is_json:
        return doc.Object(swagger_schema)

    return swagger_schema


def open_api_schemas_params(schema: Schema, location="query") -> List[Parameter]:
    """
    Generate swagger documentation for query-parameters from a Marshmallow schema.

    Args:
        schema (Schema): The marshmallow schema object.

    Returns:
        list: List of openapi Field-nested objects.
    """

    params = []

    # Generating swagger parameters for each field in the marshmallow schema
    for field_name in schema.fields:
        field_schema = schema.fields[field_name]
        params.append(
            Parameter(
                field_name,
                marshmallow_to_openapi(field_name, field_schema),
                location=location,
            )
        )

    return params


def marshmallow_to_openapi(field_name: str, field_schema: fields.Field) -> doc.Schema:
    """
    Map a Marshmallow field to an OpenAPI field.

    Args:
        field_name (str): The field name.
        field_schema (fields.Field): The marshmallow field.

    Returns:
        doc.Schema: The openapi field.
    """

    field_type = type(field_schema)
    doc_type = MAP_MARSHMALLOW_IN_OPEN_API.get(field_type, doc.String)
    swagger_type = None

    if isinstance(field_schema, fields.Nested):
        schema = open_api_schemas(field_schema.schema, is_json=True)
        swagger_type = doc_type(schema, required=field_schema.required)

    elif isinstance(field_schema, fields.List):
        if isinstance(field_schema.inner, fields.Nested):
            schema = open_api_schemas(field_schema.inner.schema, is_json=True)
            swagger_type = doc.Array(schema)
        else:
            inner_type = MAP_MARSHMALLOW_IN_OPEN_API.get(
                type(field_schema.inner), doc.String
            )
            swagger_type = doc_type(
                inner_type(), name=field_name, required=field_schema.required
            )

    else:
        if isinstance(field_schema, fields.Enum):
            swagger_type = doc.Schema.make(field_schema.enum)
        else:
            swagger_type = doc_type(name=field_name, required=field_schema.required)

    return swagger_type
