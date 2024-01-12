import os
from pathlib import Path

import dotenv
from pydantic import BaseModel

dirname = Path(__file__).parent.absolute()
dotenv.load_dotenv()


class _ExtractorConfig(BaseModel):
    base_output_path: Path = Path(dirname, "../../src/genai/_generated")
    schema_aliases_path: Path = Path(dirname, "schema_aliases.yaml")
    output_models_filename: str = "api.py"
    endpoint_models_filename: str = "endpoints.py"
    endpoint_version_model_name: str = "ApiEndpointVersionMap"
    endpoint_model_name: str = "ApiEndpointMap"
    base_model_class: str = "genai._types.ApiBaseModel"
    openapi_yaml_endpoint_url: str
    save_schemas_locally: bool = False


ExtractorConfig = _ExtractorConfig(
    openapi_yaml_endpoint_url=os.environ["GENAI_OPENAPI_YAML_ENDPOINT"],
    save_schemas_locally=str(os.environ.get("SAVE_SCHEMAS_LOCALLY", "false")).lower() == "true",
)
