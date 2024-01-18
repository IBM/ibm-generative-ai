import logging
import shutil
from contextlib import nullcontext as does_not_raise
from filecmp import dircmp
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from docs_examples_generator.config import GeneratorConfig
from docs_examples_generator.main import run as generate
from pydantic import BaseModel


class TestCase(BaseModel):
    config: GeneratorConfig


def assert_same_directories(a: Path, b: Path) -> None:
    def _has_diff(dcmp) -> bool:
        differences = dcmp.left_only + dcmp.right_only + dcmp.diff_files
        if differences:
            return True

        return any(_has_diff(subdcmp) for subdcmp in dcmp.subdirs.values())

    cmp = dircmp(a, b)
    if _has_diff(cmp):
        cmp.report_full_closure()
        raise AssertionError("Differences found, see log above.")


@pytest.mark.parametrize(
    "name,expectation",
    [("valid_case", does_not_raise()), ("invalid_case", pytest.raises(ValueError, match="Missing docstring *"))],
)
@pytest.mark.unit
def test_docs_examples_generator(name: str, expectation):
    assets_dir = Path(Path(__file__).parent.resolve(), "assets", name)
    expected_output_directory = Path(assets_dir, "output")
    expected_input_directory = Path(assets_dir, "input")

    with TemporaryDirectory() as tmp_dir:
        output_directory = Path(tmp_dir, "output")
        output_directory.mkdir()
        assert output_directory.exists()

        input_directory = Path(tmp_dir, "input")
        shutil.copytree(expected_input_directory, input_directory)
        assert input_directory.exists()

        config = GeneratorConfig(
            output_directory=output_directory,
            input_directory=input_directory,
            module_name="valid_module",
            exclude={"nested/blacklisted.py"},
        )

        with expectation:
            generate(config)

        if isinstance(expectation, does_not_raise):
            if not expected_output_directory.exists():
                logging.warning("Expected output directory does not exists! Verify manually.")
                shutil.copytree(output_directory, expected_output_directory)
            else:
                assert_same_directories(output_directory, expected_output_directory)
