from contextvars import ContextVar
from pathlib import Path

import dotenv
from pydantic import BaseModel

dirname = Path(__file__).parent.absolute()
dotenv.load_dotenv()


class ChangelogConfig(BaseModel):
    output_file_path: Path = Path(dirname, "../../documentation/source/changelog.rst")
    author_names_mapping_path: Path = dirname / Path("authors_by_name.yaml")
    mustache_template_path: Path = dirname / Path("mustache_rst.tpl")
    gitchangelog_config_path: Path = dirname / Path("gitchangelog_config.py")
    repo_url: str = "https://github.com/IBM/ibm-generative-ai"
    repo_api_url: str = "https://api.github.com/repos/IBM/ibm-generative-ai"
    unreleased_version_label: str = "(unreleased)"  # Changing this requires manual update in existing changelog


DefaultChangelogConfig = ChangelogConfig()
config_context_var = ContextVar[ChangelogConfig]("config", default=DefaultChangelogConfig)
