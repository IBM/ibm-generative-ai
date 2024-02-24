import tempfile
import time
from pathlib import Path

import httpx
import yaml
from _common.logger import get_logger
from datamodel_code_generator import DataModelType, InputFileType, LiteralType, OpenAPIScope, PythonVersion, generate
from dotenv import load_dotenv

import types_generator.formatter as code_formatter
from types_generator.config import ExtractorConfig
from types_generator.extractor import ApiEndpoint, extract_endpoints
from types_generator.schema_transformer import SchemaOverrides, transform_schema
from types_generator.utils import dump_model, serialize_model, serialize_model_definition

load_dotenv()

dirname = Path(__file__).parent.absolute()
logger = get_logger(__name__)


def load_openapi_schema(url: str):
    with httpx.Client() as client:
        response = client.get(url=url)
        response.raise_for_status()
        content = response.content.decode("utf-8")
        return yaml.safe_load(content)


def generate_models(schema_path: Path, output: Path):
    if output.exists():
        output.unlink()

    generate(
        input_=schema_path.resolve(),
        input_filename=f"{time.strftime('%Y-%m-%d')}_openapi_schema",
        input_file_type=InputFileType.OpenAPI,
        # replaces prefix of field names starting with special characters (including '_') by this value
        special_field_name_prefix=ExtractorConfig.private_field_name,
        output=output,
        output_model_type=DataModelType.PydanticV2BaseModel,
        apply_default_values_for_required_fields=True,
        openapi_scopes=[OpenAPIScope.Parameters, OpenAPIScope.Paths, OpenAPIScope.Schemas],
        use_operation_id_as_name=True,
        aliases={"date": "date_"},
        reuse_model=False,
        target_python_version=PythonVersion.PY_39,
        base_class=ExtractorConfig.base_model_class,
        enum_field_as_literal=LiteralType.One,
        use_one_literal_as_default=True,
        capitalise_enum_members=True,
        use_subclass_enum=True,
        collapse_root_models=True,
        disable_appending_item_suffix=True,
        field_constraints=True,
        disable_timestamp=True,
        custom_template_dir=Path(dirname, "assets/codegen/templates"),
        keep_model_order=False,
        use_generic_container_types=False,
        use_standard_collections=True,
        use_field_description=True,
        use_union_operator=False,
        custom_formatters=[code_formatter.__name__],
    )


def run():
    try:
        logger.info(f"Loading OpenAPI Schema (YAML) from '{ExtractorConfig.openapi_yaml_endpoint_url}'")
        schema = load_openapi_schema(url=ExtractorConfig.openapi_yaml_endpoint_url)

        if ExtractorConfig.save_schemas_locally:
            target = Path(tempfile.gettempdir(), "genai_open_api_schema_source.yml")
            logger.info(f"Saving original OpenAPI Schema to {target.resolve()}")
            with target.open("w") as stream:
                yaml.dump(schema, stream=stream, default_flow_style=False)

        logger.info("Transforming schema...")
        with open(ExtractorConfig.schema_aliases_path) as f:
            schema_overrides = SchemaOverrides.model_validate(yaml.safe_load(f))
        transform_schema(schema, schema_overrides, ExtractorConfig.operation_id_prefix)

        endpoints_output = Path(ExtractorConfig.base_output_path, ExtractorConfig.endpoint_models_filename)
        logger.info(f"Saving extracted endpoints information to '{endpoints_output.resolve()}'")
        dump_model(
            target=endpoints_output,
            serialized="\n\n".join(
                [
                    serialize_model_definition(
                        ApiEndpoint,
                    ),
                    *[
                        serialize_model(
                            name=model.class_name,
                            base_model=ApiEndpoint.__name__,
                            model=model.model_dump(exclude_none=True, exclude={"class_name"}),
                        )
                        for model in extract_endpoints(schema, schema_overrides.endpoint_aliases)
                    ],
                ]
            ),
        )

        if ExtractorConfig.save_schemas_locally:
            target = Path(tempfile.gettempdir(), "genai_open_api_schema.yml")
            logger.info(f"Saving updated OpenAPI Schema to {target.resolve()}")
            with target.open("w") as stream:
                yaml.dump(schema, stream=stream, default_flow_style=False)

        with tempfile.NamedTemporaryFile(suffix=".yml") as tmp:
            logger.info("Saving schema to a temporary file")

            with open(tmp.name, "w") as stream:
                yaml.dump(schema, stream, default_flow_style=False)

            models_output = Path(ExtractorConfig.base_output_path, ExtractorConfig.output_models_filename)

            logger.info("Running DataModel Code Generator")
            logger.info(f"Output will be saved to '{models_output.resolve()}'")

            generate_models(
                schema_path=Path(tmp.name),
                output=models_output,
            )

            logger.info("Done!")
    except Exception as e:
        logger.error(e, exc_info=True)
        exit(1)


if __name__ == "__main__":
    run()
