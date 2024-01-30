import logging
import pathlib
import runpy
import sys

import pytest

logger = logging.getLogger(__name__)

all_scripts = list(pathlib.Path(__file__, "../../../examples").resolve().rglob("*.py"))
ignore_files = {
    "__init__.py",
    # exclude long-running examples (resort to integration tests)
    "huggingface_agent.py",
    "tune.py",
    "parallel_processing.py",
    "chroma_db_embedding.py",
}
skip_for_python_3_12 = {
    # These files are skipped for python >= 3.12 because transformers library cannot be installed
    "local_server.py",
    "huggingface_agent.py",
}

scripts_lt_3_12 = {script for script in all_scripts if script.name not in ignore_files | skip_for_python_3_12}
scripts_3_12 = {script for script in all_scripts if script.name in skip_for_python_3_12}


def idfn(val):
    return pathlib.Path(val).name


@pytest.mark.e2e
def test_finds_examples():
    assert all_scripts


@pytest.mark.e2e
@pytest.mark.skipif(sys.version_info >= (3, 12), reason="transformers can't be installed for python 3.12 yet")
@pytest.mark.parametrize("script", scripts_3_12, ids=idfn)
def test_example_execution_for_python_lt_3_12(script):
    logger.info(f"Executing Example script: {script}")
    runpy.run_path(str(script), run_name="__main__")


@pytest.mark.e2e
@pytest.mark.parametrize("script", scripts_lt_3_12, ids=idfn)
def test_example_execution(script):
    logger.info(f"Executing Example script: {script}")
    runpy.run_path(str(script), run_name="__main__")
