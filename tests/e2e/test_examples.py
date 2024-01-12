import logging
import pathlib
import runpy

import pytest

logger = logging.getLogger(__name__)

all_scripts = list(pathlib.Path(__file__, "../../../examples").resolve().rglob("*.py"))
ignore_files = {"huggingface_agent.py", "tune.py"}  # exclude long-running examples (resort to integration tests)
scripts = {script for script in all_scripts if script.name not in ignore_files}


def idfn(val):
    return pathlib.Path(val).name


@pytest.mark.e2e
def test_finds_examples():
    assert all_scripts


@pytest.mark.e2e
@pytest.mark.parametrize("script", scripts, ids=idfn)
def test_example_execution(script):
    logger.info(f"Executing Example script: {script}")
    runpy.run_path(str(script), run_name="__main__")
