# sanic-openapi-ext

**sanic-openapi-ext** is a Python package that provides a simplified method for generating OpenAPI (Swagger) documentation from Marshmallow schemas in a Sanic web application. It offers an explicit mapping between Marshmallow fields and OpenAPI fields, which aids in the automatic generation of precise API documentation.

## Features
- Automatic generation of OpenAPI (Swagger) documentation from Marshmallow schemas.
- Handles different types of Marshmallow fields including basic types, complex types, dates, and numbers.
- Supports conversion of nested fields and lists.

## Installation
```
pip install sanic-openapi-ext
```

## Quick Start
Here's a simple example of how to use sanic-openapi-ext:

```python
from marshmallow import Schema, fields
from sanic_openapi_ext import open_api_schemas

class UserSchema(Schema):
    name = fields.Str()
    birthdate = fields.Date()

# Generate OpenAPI schema from Marshmallow schema
user_openapi_schema = open_api_schemas(UserSchema())
```

## Examples
#### Input/output simple schema object

Parameter represents query params as `ExampleSchema`

Response represents json output as `ExampleSchema`

```python
from marshmallow import Schema, fields
from sanic import Sanic, response
from sanic_openapi_ext import open_api_schemas, open_api_schemas_params
from sanic_ext import openapi
from sanic_ext.extensions.openapi.definitions import Response


class ExampleSchema(Schema):
    name = fields.Str(required=True)
    age = fields.Integer(required=True)


app = Sanic("MyHelloWorldApp")


@app.get("/")
@openapi.definition(
    parameter=open_api_schemas_params(ExampleSchema()),
    response=[
        Response(open_api_schemas(ExampleSchema(), is_json=True), status=200),
    ],
)
async def get_and_return_example_schema(request):
    result = ExampleSchema().dump({"name": "John Doe", "age": 42})
    return response.json({"success": 200, "result": result})

```
![Sanic OpenAPI spec screenshot](https://i.imgur.com/dTI0DLb.png)


#### Input schema object with enum, output - nested schema with enum

Parameter represents header params as `ExampleSchema`

Response represents json output as list of `ExampleSchema`

```python
from enum import Enum
from marshmallow import Schema, fields
from sanic import Sanic, response
from sanic_openapi_ext import open_api_schemas, open_api_schemas_params
from sanic_ext import openapi
from sanic_ext.extensions.openapi.definitions import Response


class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3


class ExampleSchema(Schema):
    text = fields.Str()
    color = fields.Enum(Color)


class ExampleListSchema(Schema):
    items = fields.List(fields.Nested(ExampleSchema))


app = Sanic("MyHelloWorldApp")


@app.get("/")
@openapi.definition(
    parameter=open_api_schemas_params(ExampleSchema(), location="header"),
    response=[
        Response(open_api_schemas(ExampleListSchema(), is_json=True), status=200),
    ],
)
async def get_and_return_example_schema(request):
    result = ExampleListSchema().dump([{"text": "Lorem ipsum", "color": 1}], many=True)
    return response.json({"success": 200, "result": result})
```
![Sanic OpenAPI spec screenshot](https://i.imgur.com/9HaTENf.png)

## Mapping reference
Below is a mapping table of how Marshmallow fields are converted into OpenAPI fields:

| Marshmallow Field | OpenAPI Field |
| ------------------ | ------------- |
| DateTime           | doc.DateTime |
| Date               | doc.Date |
| Time               | doc.Time |
| Integer,Int        | doc.Integer |
| Float              | doc.Float |
| Decimal            | doc.String |
| String, Str        | doc.String |
| Boolean, Bool      | doc.Boolean |
| Enum               | doc.Schema |
| List               | doc.Array |
| Nested             | doc.Object |

Note:

- If the `many` attribute of the Marshmallow schema is set to `True`, or if the input `many` attribute is `True`, a doc.List will be returned.
- If the input `is_json` attribute is `True`, a doc.JsonBody will be returned.
- If the field is of type `fields.Enum`, a `doc.Schema`, which accepts the enumeration, is returned.
- If the field is of type `fields.List`, the inner_field is accessed. If the inner_field is a `fields.Nested`, a `doc.Object` is returned with the properties of the nested schema. If the inner_fields belong to other types, a `doc.Array` is returned with the properties of the inner type.
- For fields not listed in the table, `doc.String` is used as a default.
  
Please, remember that this mapping may vary according to the use and the specific need of the project.

# Contribute
We'd love for you to contribute to our source code and to make **sanic-openapi-ext** even better than it is today! Here are some ways you can contribute:

- by reporting bugs
- by suggesting new features
- by writing or editing documentation
- by writing specifications
- by writing code (no patch is too small, fix typos, add comments, clean up inconsistent whitespace)
- by refactoring code
- by closing issues
- by reviewing patches

# License
sanic-openapi-ext is released under the MIT license.
