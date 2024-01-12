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


@pytest.fixture
def propagate_caplog(caplog):
    logger = None

    def _propagate_caplog(name: str):
        nonlocal logger
        logger = logging.getLogger(name)
        logger.addHandler(caplog.handler)
        return caplog

    yield _propagate_caplog

    if logger:
        logger.removeHandler(caplog.handler)


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
    transform_schema(api, schema_overrides=SchemaOverrides())
    extracted_schemas = api["components"]["schemas"]
    input_schemas = process_schema_test_input.schemas
    assert extracted_schemas == {
        "TestpathCreateRequest_testproperty": input_schemas["TestpathCreateRequest_testproperty"],
        "TestpathCreate_result": {
            "properties": {
                "nested_schema": {"$ref": "#/components/schemas/TestpathCreate_result_nested_schema"},
                "prop1": {"type": "string"},
            },
            "type": "object",
        },
        "TestpathCreate_result_nested_schema": input_schemas["TestpathCreateRequest_testproperty"],
    }
    testpath_schema = api["paths"]["/testpath"]["post"]
    requestBody = testpath_schema["requestBody"]["content"]["application/json"]["schema"]
    response = testpath_schema["responses"]["200"]["content"]["application/json"]["schema"]
    assert requestBody == to_object(
        {"testproperty": {"$ref": "#/components/schemas/TestpathCreateRequest_testproperty"}}
    )
    assert response == to_object({"result": {"$ref": "#/components/schemas/TestpathCreate_result"}})

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
        "MyReusableProperty": ["TestpathCreateRequest_testproperty", "TestpathCreate_result_nested_schema"],
        "BetterNameForResult": ["TestpathCreate_result"],
    }
    transform_schema(api, SchemaOverrides(alias=schema_aliases))
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
    schema_aliases = {"Alias1": ["TestpathCreateRequest_testproperty", "TestpathCreate_result"]}
    with pytest.raises(ValueError, match="The schemas in the following group are not identical"):
        transform_schema(process_schema_test_input.api, SchemaOverrides(alias=schema_aliases))


@pytest.mark.unit
def test_transform_schema_raises_when_aliases_overlap_api(process_schema_test_input: ProcessSchemaTestInput) -> None:
    """Raises when aliases would override fully qualified API names."""
    schema_aliases = {"TestpathCreateRequest_testproperty": ["TestpathCreate_result"]}
    with pytest.raises(ValueError, match="would override openapi names: {'TestpathCreateRequest_testproperty'}"):
        transform_schema(process_schema_test_input.api, SchemaOverrides(alias=schema_aliases))


@pytest.mark.unit
def test_transform_schema_raises_when_unknown_name_is_aliased(
    process_schema_test_input: ProcessSchemaTestInput,
) -> None:
    """Raises when some name is aliased twice."""
    schema_aliases = {"42": ["the_answer_to_life_the_universe_and_everything"]}
    with pytest.raises(ValueError, match="The following schemas are not part of openapi specification"):
        transform_schema(process_schema_test_input.api, SchemaOverrides(alias=schema_aliases))


@pytest.mark.unit
def test_transform_schema_raises_when_name_is_aliased_twice(process_schema_test_input: ProcessSchemaTestInput) -> None:
    """Raises when some name is aliased twice."""
    schema_aliases = {"Alias1": ["TestpathCreate_result"], "Alias2": ["TestpathCreate_result"]}
    with pytest.raises(ValueError, match="The following names are aliased more than once:"):
        transform_schema(process_schema_test_input.api, SchemaOverrides(alias=schema_aliases))
