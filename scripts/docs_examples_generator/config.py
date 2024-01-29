import os
from pathlib import Path

import dotenv
from pydantic import BaseModel, Field

dirname = Path(__file__).parent.absolute()
dotenv.load_dotenv()


class GeneratorConfig(BaseModel):
    output_directory: Path = Path(dirname, "../../documentation/source/rst_source")
    input_directory: Path = Path(dirname, "../../examples")
    module_name: str = Field("examples", min_length=1)
    input_directory_href: str = (
        f"https://github.com/IBM/ibm-generative-ai/blob/{os.environ.get('BRANCH_NAME', 'main')}/examples"
    )
    exclude: set[str] = set()
    modules_order: dict[str, dict[str, list[int]]] = {
        "examples": [
            "examples.text",
            "examples.model",
            "examples.tune",
            "examples.prompt",
            "examples.file",
            "examples.user",
            "examples.request",
            "examples.extension",
            "examples.extra",
        ]
    }


DefaultGeneratorConfig = GeneratorConfig()
