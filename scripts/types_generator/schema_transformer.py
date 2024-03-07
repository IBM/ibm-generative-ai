import functools
import hashlib
import json
import re
from collections import Counter, defaultdict
from collections.abc import Mapping
from typing import Any, Optional, Union

import yaml
from _common.logger import get_logger
from pydantic import BaseModel

from types_generator.utils import from_camel_case_to_snake_case

Schema = dict

__all__ = ["transform_schema", "Schema"]

logger = get_logger(__name__)


class SchemaReplacement(BaseModel):
    source_name: str
    force: bool = False


class SchemaOverrides(BaseModel):
    alias: dict[str, list[str]] = {}
    replace: dict[str, Union[str, SchemaReplacement]] = {}
    private_operations: set[str] = set()
    endpoint_mapping: dict[str, str] = {}
    any_dict_to_class: set[str] = {}

    @property
    def replacements(self) -> dict[str, SchemaReplacement]:
        return {
            target: s if isinstance(s, SchemaReplacement) else SchemaReplacement(source_name=s)
            for target, s in self.replace.items()
        }


def _remove_compositions(schema: Any, *, path="", delimiter="."):
    if not schema or not isinstance(schema, Schema):
        return

    custom_keys = {"anyOf", "oneOf"}

    for key, value in list(schema.items()):
        full_path = f"{path}{delimiter}{key}".lstrip(delimiter)
        logger.debug(f"Processing '{full_path}'")

        if not value:
            continue

        if isinstance(value, Mapping):
            _remove_compositions(value, path=full_path, delimiter=delimiter)

        elif isinstance(value, list):
            if key in custom_keys:
                if all(isinstance(v, Schema) and ("required" in v or "not" in v) for v in value):
                    logger.warning(
                        f"Deleting '{full_path}' (Content: {value})",
                    )
                    del schema[key]

            for idx, v in enumerate(value):
                _remove_compositions(v, path=f"{full_path}[{idx}]", delimiter=delimiter)


def path_to_schema_name(path: str, delimiter: str) -> str:
    """
    Example::

        /users/{id}/do-something -> userIdDoSomething
    """

    path_parts = path.replace("/v2/", "").strip(delimiter).split("/")
    path = delimiter.join(part.rstrip("s") for part in path_parts)  # make singular

    def _process_parameters(value: str):
        return re.sub(
            r"\{(.*?)}",
            lambda m: from_camel_case_to_snake_case(m.group(1)),
            value,
            flags=re.MULTILINE,
        )

    def _process_hyphens(value: str):
        return re.sub(pattern=r"[-](.)", repl=lambda x: f"_{x.group(1)}", string=value, flags=re.MULTILINE)

    return functools.reduce(lambda input, fn: fn(input), [_process_hyphens, _process_parameters], path)


def to_classname(snake_string: str, public=False) -> str:
    classname = snake_string.title().replace("_", "")
    return classname if public else f"_{classname}"


def _is_any_dictionary(schema: Schema):
    return isinstance(schema, dict) and schema.get("type") == "object" and not schema.get("properties")


def _hash_schema(schema: Schema, force_hash: bool = False):
    is_hashable = force_hash or not _is_any_dictionary(schema)
    if not is_hashable:
        return None

    return hashlib.md5(json.dumps(schema, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def _get_schema_path(name: str):
    return f"#/components/schemas/{name}"


def _is_plain_string(schema: Schema):
    return schema.get("type") == "string" and schema.get("enum") is None


def _detect_type(schema: Schema) -> Optional[str]:
    type = schema.get("type", None)
    if type:
        return type
    elif schema.get("properties") is not None:
        return "object"
    elif schema.get("items") is not None:
        return "array"
    else:
        return None


def _process_schema_factory(existing_schemas: dict, name_to_alias: dict[str, str], any_dict_to_class: set[str]):  # noqa: C901
    schema_hashes: dict[str, set[str]] = defaultdict(set)
    schema_names = {""}
    schema_key = "schema"

    def _remove_non_important_properties(schema: Schema):
        schema.pop("additionalProperties", None)
        schema.pop("transform", None)

    def process_and_replace(input: Any, name: str) -> Schema:
        tmp_target = {"schema": input}
        process_schema(name, tmp_target)
        if tmp_target["schema"] is input and not _is_any_dictionary(input):
            raise ValueError(f"Failed to detect any schema for {name} ({input})")
        return tmp_target["schema"]

    def process_body(name_nested: str, body: Any):
        if isinstance(body, list):
            for idx, v in enumerate(list(body)):
                _remove_non_important_properties(v)
                nested_type = v.get("type")
                if nested_type == "object" or v.get("enum"):
                    body[idx] = process_and_replace(v, name_nested)
                elif nested_type == "array" and v.get("items") and not _is_plain_string(v.get("items")):
                    v["items"] = process_and_replace(v["items"], name_nested)
            return

        if not isinstance(body, Schema):
            return
        _remove_non_important_properties(body)

        nest_keys = {"anyOf", "oneOf", "items"}
        for k_top, v_top in sorted(body.items()):
            if k_top in nest_keys:
                process_body(name_nested, v_top)
                continue
            elif k_top == "properties":
                assert isinstance(v_top, Schema)
                _remove_non_important_properties(v_top)
                for k, v in v_top.items():
                    if not isinstance(v, Schema):
                        continue

                    new_name = f"{name_nested}_{k}"
                    type = _detect_type(v)

                    if not type:
                        process_body(new_name, v)
                    elif type == "object":
                        assert isinstance(v, Schema)
                        v_top[k] = process_and_replace(v, new_name)
                    elif type == "string" and v.get("enum"):
                        v.pop("nullable", None)
                        assert isinstance(v.get("enum"), list)
                        v_top[k] = process_and_replace(v, new_name)
                    elif type == "array" and v.get("items") and not _is_plain_string(v.get("items")):
                        assert isinstance(v.get("items"), Schema)
                        v["items"] = process_and_replace(v.get("items"), new_name)

    def _get_unique_name(schema_name: str, counter=1):
        if schema_name not in schema_names:
            return schema_name
        return _get_unique_name(f"{schema_name}{counter}", counter + 1)

    def process_schema(
        schema_name: str,
        parent: dict,
        *,
        extract_top_level=True,
    ):
        """Extracts inline schemas and replaces them with references."""
        schema = parent.get(schema_key)
        if (
            not isinstance(schema, Schema)
            or schema.get("$ref")
            or all(option == {"type": "null"} or option.get("$ref") for option in schema.get("anyOf", [{}]))
        ):
            return

        process_body(schema_name, schema)

        if not extract_top_level:
            if schema.get("enum") is None:
                return

        nullable = schema.pop("nullable", False)
        schema_hash = _hash_schema(schema, force_hash=schema_name in any_dict_to_class)
        if schema_hash is None:
            return
        elif schema_name not in schema_hashes[schema_hash]:
            # schema with this name does not yet exist
            new_name = _get_unique_name(schema_name)
            if new_name != schema_name:
                logger.warning(f"Schema Name '{schema_name}' already exists. Changing to '{new_name}'")
            schema_name = new_name

        # Store original schema name for _get_unique_name and alias validation
        schema_hashes[schema_hash].add(schema_name)
        schema_names.add(schema_name)

        # Rename schema according to alias mapping
        schema_alias = name_to_alias.get(schema_name, schema_name)

        existing_schemas[schema_alias] = schema
        ref = {"$ref": _get_schema_path(schema_alias)}
        if nullable:
            ref = {"anyOf": [{"type": "null"}, ref]}
        parent[schema_key] = ref

    return process_schema, schema_hashes


http_method_mapper = {
    "post": "create",
    "get": "retrieve",
    "put": "update",
    "patch": "patch",
    "delete": "delete",
}


def _validate_schema_aliases(schema_hash_to_names: dict[str, set[str]], schema_aliases: dict[str, list[str]]):
    name_to_alias = {name: alias for alias, name_group in schema_aliases.items() for name in name_group}
    schema_name_to_hash = {v: k for k, group in schema_hash_to_names.items() for v in group}

    # 1) Can't use existing schema name as alias
    if duplicates := schema_aliases.keys() & schema_name_to_hash.keys():
        raise ValueError(f"Schema aliases are not unique, the following would override openapi names: {duplicates}")

    # 2) Can't have two different aliases for the same schema
    names_count = Counter(name for name_group in schema_aliases.values() for name in name_group)
    if duplicate_names := {alias: count for alias, count in names_count.items() if count > 1}:
        raise ValueError(f"The following names are aliased more than once: {duplicate_names}")

    # 3) Check identical schemas are unified under one alias
    schema_duplicities = {}
    aliased_names = set(name_to_alias)
    for hash, names_group in schema_hash_to_names.items():
        if hash is None:
            continue
        names = {name for name in names_group if name not in aliased_names}
        names |= {f"{name_to_alias[name]} [alias]" for name in names_group if name in aliased_names}
        if len(names) > 1:
            schema_duplicities[hash] = list(names)
    if schema_duplicities:
        logger.warning(f"The following duplicate schemas are not unified: \n{yaml.dump(schema_duplicities)}")

    for alias_group in schema_aliases.values():
        # 4) Can't use alias for unknown schemas
        if unknown_schemas := {schema_name for schema_name in alias_group if schema_name not in schema_name_to_hash}:
            raise ValueError(f"The following schemas are not part of openapi specification: {unknown_schemas}")

        # 5) Can't group different schemas under one alias
        hashes = {schema_name_to_hash[schema_name] for schema_name in alias_group}
        if len(hashes) != 1:
            collisions = {name: f"hash: {schema_name_to_hash[name]}" for name in alias_group}
            raise ValueError(
                f"The schemas in the following group are not identical: {collisions}",
                "Please check the schema differences or if all sub-schemas are correctly grouped under alias.",
            )


def _validate_schema_replacements(api: Schema, schema_replacements: dict[str, SchemaReplacement]):
    schemas = api["components"]["schemas"]
    sources = [v.source_name for v in schema_replacements.values()]
    if missing_schemas := {s for s in schema_replacements.keys() | sources if s not in schemas}:
        raise ValueError(f"The following schemas are missing: {missing_schemas}")

    if duplicates := {name for name, count in Counter(sources).items() if count > 1}:
        raise ValueError(f"The following schemas are replaced more than once: {duplicates}")

    # Very rough check if schemaas appear the same on the surface
    for target_name, replacement in schema_replacements.items():
        if replacement.force:
            logger.warning(f"Force replacing {target_name} by {replacement.source_name}.")
            continue

        source_name = replacement.source_name
        source_schema, target_schema = schemas[source_name], schemas[target_name]
        if "properties" in source_schema:
            if (
                "properties" not in target_schema
                or source_schema["properties"].keys() ^ target_schema["properties"].keys()
            ):
                raise ValueError(f"Schemas {source_name} and {target_name} are not equivalent!")
        elif "enum" in source_schema:
            if "enum" not in target_schema or source_schema["enum"] != target_schema["enum"]:
                raise ValueError(f"Schemas {source_name} and {target_name} are not equivalent!")
        else:
            raise NotImplementedError(f"Overriding type schema {source_schema} is not yet supported.")


def _replace_recursive(obj: Union[dict, list], property: str, mapping: dict[str, str]):
    if isinstance(obj, list):
        for item in obj:
            _replace_recursive(item, property, mapping)
    elif isinstance(obj, dict):
        for key, value in obj.items():
            if key == property:
                obj[key] = mapping.get(value, value)
            _replace_recursive(value, property, mapping)


def _replace_schemas(api: Schema, schema_replacements: dict[str, SchemaReplacement]):
    for target, replacement in schema_replacements.items():
        api["components"]["schemas"][target] = api["components"]["schemas"][replacement.source_name]
        del api["components"]["schemas"][replacement.source_name]
    src_to_dst = {_get_schema_path(src.source_name): _get_schema_path(dst) for dst, src in schema_replacements.items()}
    _replace_recursive(api, "$ref", src_to_dst)


def transform_schema(api: Schema, schema_overrides: SchemaOverrides, operation_id_prefix: str):
    """
    1. Remove Simple Composites (oneOf, anyOf, allOf)
    2. Extract request/response objects into standalone schemas
    """
    _remove_compositions(api)

    if "components" not in api:
        api["components"] = {}
    if "schemas" not in api["components"]:
        api["components"]["schemas"] = {}

    name_to_alias = {name: alias for alias, name_group in schema_overrides.alias.items() for name in name_group}
    process_schema, schema_hashes = _process_schema_factory(
        existing_schemas=api["components"]["schemas"],
        name_to_alias=name_to_alias,
        any_dict_to_class=schema_overrides.any_dict_to_class,
    )

    # Process and improve existing schemas
    for name, schema in sorted(api["components"]["schemas"].items()):
        process_schema(name, {"schema": schema}, extract_top_level=False)

    private_operations = schema_overrides.private_operations.copy()
    # Process all existing paths
    for path, http_methods in sorted(api.get("paths", {}).items()):
        base_schema_name = path_to_schema_name(schema_overrides.endpoint_mapping.get(path, path), delimiter="_")

        for http_method, properties in sorted(http_methods.items()):
            assert isinstance(properties, dict)

            http_method = http_method_mapper[http_method]
            assert http_method

            endpoint_class_name = to_classname(f"{base_schema_name}_{http_method.title()}", public=True)

            if endpoint_class_name in private_operations:
                private_operations.remove(endpoint_class_name)
                endpoint_class_name = f"_{endpoint_class_name}"

            # Adding operationId instructs the generator to use given name instead generated one
            properties["operationId"] = f"{operation_id_prefix}{endpoint_class_name}"

            # Process request parameters
            for parameter in list(properties.get("parameters", [])):
                # Set default value for version ('enum' may not exists, but 'example' is guaranteed to be valid)
                if parameter.get("in") == "query" and parameter.get("name") == "version":
                    schema = parameter.get("schema")
                    if not schema.get("enum"):
                        schema["enum"] = [schema.get("example")]
                    assert len(schema["enum"]) == 1
                    schema.pop("example", None)
                    continue

                # Fix for generator not using default value for required parameters
                if parameter.get("required") and parameter.get("schema", {}).get("default") is not None:
                    del parameter["required"]

                name = to_classname(f"{base_schema_name}_{http_method.title()}_request_params_{parameter.get('name')}")
                process_schema(name, parameter, extract_top_level=False)

            # Process schemas for request bodies
            for value in properties.get("requestBody", {}).get("content", {}).values():
                name = to_classname(f"{base_schema_name}_{http_method.title()}_request")
                process_schema(name, value, extract_top_level=False)

            # Process schemas for responses
            for status_code, response in properties.get("responses", {}).items():
                for content_type, value in response.get("content", {}).items():
                    if content_type == "text/event-stream":
                        assert isinstance(value, dict)
                        schema = value["schema"]
                        assert isinstance(schema, dict)
                        if schema.get("type") == "array" and schema.get("items"):
                            items = schema.get("items", {})
                            schema.pop("type")
                            schema.pop("items")
                            schema.pop("format")
                            schema.update(items)

                    suffix = f"_{status_code}" if str(status_code) != "200" else ""
                    name = to_classname(f"{base_schema_name}_{http_method.title()}{suffix}")
                    process_schema(name, value, extract_top_level=False)
    if private_operations:
        raise ValueError(f"The following operations are not in schema: {list(private_operations)}")
    _validate_schema_aliases(schema_hashes, schema_overrides.alias)
    _validate_schema_replacements(api, schema_overrides.replacements)
    _replace_schemas(api, schema_overrides.replacements)
