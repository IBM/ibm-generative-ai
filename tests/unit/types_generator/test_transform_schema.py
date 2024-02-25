import logging
from typing import Any, NamedTuple

import pytest
from types_generator.schema_transformer import SchemaOverrides, transform_schema


class ProcessSchemaTestInput(NamedTuple):
    api: dict[str, Any]
    schemas: dict[str, dict[str, Any]]


def response_body_properties(data: dict[str, Any], return_code: int = 200) -> dict[str, Any]:
    return {str(return_code): to_json_content(data)}


def to_json_content(data: dict[str, Any]) -> dict[str, Any]:
    return {"content": {"application/json": {"schema": to_object(data)}}}


def to_object(obj_properties):
    return {"properties": obj_properties, "type": "object"}


OPERATION_ID_PREFIX = "TESTOPERATIONID"


@pytest.fixture
def process_schema_test_input() -> ProcessSchemaTestInput:
    TestpathCreate_result = to_object(
        {"prop1": {"type": "string"}, "nested_schema": to_object({"prop2": {"type": "string"}})}
    )
    TestpathCreateRequest_testproperty = to_object({"prop2": {"type": "string"}})
    return ProcessSchemaTestInput(
        api={
            "components": {"schemas": {}},
            "paths": {
                "/testpath": {
                    "post": {
                        "requestBody": to_json_content({"testproperty": TestpathCreateRequest_testproperty}),
                        "responses": {"200": to_json_content({"result": TestpathCreate_result})},
                    }
                }
            },
        },
        schemas={
            "TestpathCreate_result": TestpathCreate_result,
            "TestpathCreateRequest_testproperty": TestpathCreateRequest_testproperty,
        },
    )


@pytest.mark.unit
def test_transform_schema_no_aliases(process_schema_test_input: ProcessSchemaTestInput, propagate_caplog) -> None:
    """Extracts all schemas with fully qualified names."""
    caplog = propagate_caplog("types_generator.schema_transformer")
    api, input_schemas = process_schema_test_input
    transform_schema(api, SchemaOverrides(), OPERATION_ID_PREFIX)
    extracted_schemas = api["components"]["schemas"]
    input_schemas = process_schema_test_input.schemas
    assert extracted_schemas == {
        "_TestpathCreateRequest_testproperty": input_schemas["TestpathCreateRequest_testproperty"],
        "_TestpathCreate_result": {
            "properties": {
                "nested_schema": {"$ref": "#/components/schemas/_TestpathCreate_result_nested_schema"},
                "prop1": {"type": "string"},
            },
            "type": "object",
        },
        "_TestpathCreate_result_nested_schema": input_schemas["TestpathCreateRequest_testproperty"],
    }
    testpath_schema = api["paths"]["/testpath"]["post"]
    requestBody = testpath_schema["requestBody"]["content"]["application/json"]["schema"]
    response = testpath_schema["responses"]["200"]["content"]["application/json"]["schema"]
    assert requestBody == to_object(
        {"testproperty": {"$ref": "#/components/schemas/_TestpathCreateRequest_testproperty"}}
    )
    assert response == to_object({"result": {"$ref": "#/components/schemas/_TestpathCreate_result"}})

    # Warn about non-unified schemas
    with caplog.at_level(logging.WARNING):
        assert "The following duplicate schemas are not unified:" in caplog.text
        assert "TestpathCreateRequest_testproperty" in caplog.text
        assert "TestpathCreate_result_nested_schema" in caplog.text


@pytest.mark.unit
def test_transform_schema_correct_aliases(process_schema_test_input: ProcessSchemaTestInput, propagate_caplog) -> None:
    """Extracts all schemas with fully qualified names."""
    caplog = propagate_caplog("types_generator.schema_transformer")
    api, input_schemas = process_schema_test_input
    schema_aliases = {
        "MyReusableProperty": ["_TestpathCreateRequest_testproperty", "_TestpathCreate_result_nested_schema"],
        "BetterNameForResult": ["_TestpathCreate_result"],
    }
    transform_schema(api, SchemaOverrides(alias=schema_aliases), OPERATION_ID_PREFIX)
    extracted_schemas = api["components"]["schemas"]
    input_schemas = process_schema_test_input.schemas
    assert extracted_schemas == {
        "MyReusableProperty": input_schemas["TestpathCreateRequest_testproperty"],
        "BetterNameForResult": {
            "properties": {
                "nested_schema": {"$ref": "#/components/schemas/MyReusableProperty"},
                "prop1": {"type": "string"},
            },
            "type": "object",
        },
    }
    # Warn about non-unified schemas
    with caplog.at_level(logging.WARNING):
        assert caplog.text == ""


@pytest.mark.unit
def test_transform_schema_raises_when_aliases_collide(process_schema_test_input: ProcessSchemaTestInput) -> None:
    """Raises when aliases would merge two distinct schemas."""
    schema_aliases = {"Alias1": ["_TestpathCreateRequest_testproperty", "_TestpathCreate_result"]}
    with pytest.raises(ValueError, match="The schemas in the following group are not identical"):
        transform_schema(process_schema_test_input.api, SchemaOverrides(alias=schema_aliases), OPERATION_ID_PREFIX)


@pytest.mark.unit
def test_transform_schema_raises_when_aliases_overlap_api(process_schema_test_input: ProcessSchemaTestInput) -> None:
    """Raises when aliases would override fully qualified API names."""
    schema_aliases = {"_TestpathCreateRequest_testproperty": ["_TestpathCreate_result"]}
    with pytest.raises(ValueError, match="would override openapi names: {'_TestpathCreateRequest_testproperty'}"):
        transform_schema(process_schema_test_input.api, SchemaOverrides(alias=schema_aliases), OPERATION_ID_PREFIX)


@pytest.mark.unit
def test_transform_schema_raises_when_unknown_name_is_aliased(
    process_schema_test_input: ProcessSchemaTestInput,
) -> None:
    """Raises when some name is aliased twice."""
    schema_aliases = {"42": ["the_answer_to_life_the_universe_and_everything"]}
    with pytest.raises(ValueError, match="The following schemas are not part of openapi specification"):
        transform_schema(process_schema_test_input.api, SchemaOverrides(alias=schema_aliases), OPERATION_ID_PREFIX)


@pytest.mark.unit
def test_transform_schema_raises_when_name_is_aliased_twice(process_schema_test_input: ProcessSchemaTestInput) -> None:
    """Raises when some name is aliased twice."""
    schema_aliases = {"Alias1": ["TestpathCreate_result"], "Alias2": ["TestpathCreate_result"]}
    with pytest.raises(ValueError, match="The following names are aliased more than once:"):
        transform_schema(process_schema_test_input.api, SchemaOverrides(alias=schema_aliases), OPERATION_ID_PREFIX)


@pytest.mark.unit
@pytest.mark.parametrize("is_private", [True, False])
def test_transform_schema_correctly_sets_operation_ids(
    process_schema_test_input: ProcessSchemaTestInput, is_private
) -> None:
    api, input_schemas = process_schema_test_input
    schema_overrides = SchemaOverrides(private_operations={"TestpathCreate"}) if is_private else SchemaOverrides()
    transform_schema(api, schema_overrides, OPERATION_ID_PREFIX)
    private_prefix = "_" if is_private else ""
    expected_operation_id = f"{OPERATION_ID_PREFIX}{private_prefix}TestpathCreate"
    assert api["paths"]["/testpath"]["post"]["operationId"] == expected_operation_id


@pytest.mark.unit
def test_transform_schema_rename_endpoint(process_schema_test_input: ProcessSchemaTestInput) -> None:
    api, input_schemas = process_schema_test_input
    schema_overrides = SchemaOverrides(
        endpoint_aliases={
            "/testpath": "/beta/newpath",
        }
    )
    transform_schema(api, schema_overrides, OPERATION_ID_PREFIX)
    assert api["paths"]["/testpath"]["post"]["operationId"] == f"{OPERATION_ID_PREFIX}BetaNewpathCreate"
