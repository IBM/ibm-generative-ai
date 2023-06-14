import os
import pathlib
import shutil

import pytest


@pytest.mark.extension
class TestHuggingFace:
    def setup_method(self):
        self.path = pathlib.Path(__file__).parent.resolve()
        self.asset_path = pathlib.Path(__file__, "..", "..", "assets").resolve()

    def file_contains_string(self, prompt: str, path: str):
        with open(path + "/data-00000-of-00001.arrow", "rb") as f:
            if prompt.encode() in f.read():
                return True

    def test_huggingface(self, tmp_path):
        import genai.extensions.huggingface  # noqa
        from genai.prompt_pattern import PromptPattern

        datafile = pathlib.Path(self.asset_path, "age-gender.csv").resolve()

        # flake8: noqa
        template = """
            The age of the individual is {{0}}.
            The sex of the individual is {{1}}.
        """

        prompt = PromptPattern.from_str(template)

        list_of_prompts = prompt.sub_all_from_csv(csv_path=datafile, col_to_var="infer", headers=False)

        hfdataset = pathlib.Path(self.asset_path, "hf-dataset").resolve()

        prompt.huggingface.save_dataset(list_of_prompts, hfdataset)

        assert self.file_contains_string("The age of the individual is 31.", str(hfdataset))
        assert self.file_contains_string("The sex of the individual is female.", str(hfdataset))
        assert os.path.exists(hfdataset)

    def teardown_method(self):
        shutil.rmtree(pathlib.Path(self.asset_path, "hf-dataset").resolve())
