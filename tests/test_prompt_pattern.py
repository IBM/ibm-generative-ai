import json
import os
import pathlib
from unittest.mock import patch

import pytest

from genai.prompt_pattern import PromptPattern


@pytest.mark.unit
class TestPromptPattern:
    def setup_method(self):
        self.path = pathlib.Path(__file__).parent.resolve()
        self.asset_path = str(self.path) + os.sep + "assets" + os.sep

    def asset(self, name):
        with open(self.asset_path + name, "r", encoding="utf-8") as file:
            return file.read()

    def test_validate_yaml(self):
        pt = PromptPattern.from_file(self.asset_path + "capital-qa.yaml")
        assert pt.validate() is True

    def test_validate_local_yaml_prompt(self):
        pt = PromptPattern.from_file(self.asset_path + "invalid-template.yaml")
        with pytest.raises(Exception) as context:
            pt.validate()
        assert "Invalid Prompt YAML. It must include 'apiVersion'." in str(context)

    def test_invalide_local_yaml_content(self):
        with pytest.raises(Exception) as context:
            PromptPattern.from_file(self.asset_path + "invalid-content-template.yaml")
        assert "Invalid Prompt YAML. It must include 'content' fields." in str(context)

    @patch("genai.PromptPattern._fetch_prompt")
    def test_validate_yaml_from_url(self, mock_yaml):
        invalid_yaml = {"content": "this is a test prompt"}
        mock_yaml.return_value = invalid_yaml

        pt = PromptPattern.from_url(url="https://yaml", token="token")
        pt.yaml = invalid_yaml

        with pytest.raises(Exception) as context:
            pt.validate()
        assert "Invalid Prompt YAML. It must include 'apiVersion'." in str(context)

    @patch("genai.PromptPattern._fetch_prompt")
    def test_validate_yaml_content_from_url(self, mock_yaml):
        invalid_yaml = {"apiVersion": "v0", "prompts": "this is a test prompt"}
        mock_yaml.return_value = invalid_yaml

        pt = PromptPattern.from_url(url="https://yaml", token="token")
        pt.yaml = invalid_yaml

        with pytest.raises(Exception) as context:
            pt.validate()
        assert "Invalid Prompt YAML. It must include 'content' fields." in str(context)

    def test_sub(self):
        pt = PromptPattern.from_file(self.asset_path + "story.yaml")
        pt.sub("company", "Star Trek Fleet Command").sub("person", "Mr.Sock")

        expected = self.asset(name="story_sub.txt")
        assert str(pt) == expected

    def test_sub_string_template(self):
        pt = PromptPattern.from_file(self.asset_path + "capital-qa.yaml")
        pt.sub("country", "Taiwan")

        expected = self.asset(name="capital-qa-sub.txt")
        assert str(pt) == expected

    def test_cache_reset(self):
        pt = PromptPattern.from_file(self.asset_path + "capital-qa.yaml")
        pt.sub("country", "Taiwan")

        expected = self.asset(name="capital-qa-sub.txt")
        assert str(pt) == expected

        pt.reset()

        assert str(pt) == self.asset(name="capital-qa-content.txt")

    def test_sub_with_string(self):
        prompt_content = (
            "Once upon a time at {{company}} there was a "
            "{{person}}. This {{person}} had ambitious but "
            "logical ideas."
        )

        expected = (
            "Once upon a time at Star Trek Fleet Command there was a "
            "Mr.Sock. This Mr.Sock had ambitious but "
            "logical ideas."
        )
        pt = PromptPattern.from_str(prompt_content)

        pt.sub("company", "Star Trek Fleet Command").sub("person", "Mr.Sock")

        assert str(pt) == expected

    def test_find_vars(self):
        pt = PromptPattern.from_file(self.asset_path + "capital-qa.yaml")
        vars = pt.find_vars()

        expected = set(["country"])
        assert vars == expected

        pt = PromptPattern.from_file(self.asset_path + "story.yaml")
        vars = pt.find_vars()

        expected = set(["company", "person"])
        assert vars == expected

        pt = PromptPattern.from_str("My {{stuff }} is {{name}} and {{ name}} means {{ name }}")
        assert pt.find_vars() == {"name", "stuff"}

    def test_private_constructor(self):
        with pytest.raises(TypeError) as context:
            PromptPattern("some_string")
        assert "PromptPattern() takes no arguments" in str(context)

    @patch("genai.PromptPattern._fetch_prompt")
    def test_from_url_and_refetch(self, mock):
        raw_prompt = "A template from far far away..."
        mock.return_value = raw_prompt

        pt = PromptPattern.from_url(url="https://url.yaml", token="some_token")

        assert pt.raw_content == raw_prompt
        assert pt.token == "some_token"

        pt.raw_content = "Another template from far away."
        pt.refetch()
        assert pt.raw_content == raw_prompt

    def test_reset(self):
        raw_prompt = "A template from far far away..."
        pt = PromptPattern.from_str(raw_prompt)
        pt.dump = None
        pt.reset()

        assert pt.dump == raw_prompt

    def test_sub_from_csv_random(self):
        pt = PromptPattern.from_file(self.asset_path + "csv_file.yaml")

        path = self.asset_path + "csv_file.csv"
        pt.sub_from_csv(
            csv_path=path,
            strategy="random",
            col_to_var={
                "col1": ["v1", "v2"],
                "col2": ["v4"],
                "col3": ["v3"],
            },
        )

        assert str(pt).replace("\n", "") == "aa,aa,cc,bb,"

    def test_sub_from_rand_row(self):
        # Test we can change only one var:col
        pt = PromptPattern.from_file(self.asset_path + "csv_file.yaml")

        path = self.asset_path + "csv_file.csv"
        pt.sub_from_csv(csv_path=path, col_to_var={"col1": ["v2"]})

        assert str(pt).replace("\n", "") == "{{v1}},aa,{{v3}},{{v4}},"

    def test_sub_from_json(self):
        with open(os.path.join(self.asset_path, "capital-qa-sub.json"), "r") as fin:
            arr = json.load(fin)
            countries = [a["pais"] for a in arr]
            capitals = [a["capitulo"] for a in arr]
        # test for sequential
        pt = PromptPattern.from_file(self.asset_path + "capital-qa-multivar.yaml")
        pt = pt.sub_from_json(
            json_path=os.path.join(self.asset_path, "capital-qa-sub.json"),
            key_to_var={"pais": ["country1", "country2", "country3"], "capitulo": ["capital1", "capital2"]},
            strategy="sequential",
            start_index=0,
            n=1,
        )
        pstr = str(pt)
        assert sum(c in pstr for c in countries) == 3
        assert sum(c in pstr for c in capitals) == 2
        pt.reset()
        pstr = str(pt)
        assert sum(c in pstr for c in countries) == 0
        assert sum(c in pstr for c in capitals) == 0
        # test for sample
        pt = pt.sub_from_json(
            json_path=os.path.join(self.asset_path, "capital-qa-sub.json"),
            key_to_var={"pais": ["country1", "country2", "country3"], "capitulo": ["capital1", "capital2"]},
            strategy="sample",
            start_index=0,
            n=1,
        )
        pstr = str(pt)
        assert sum(c in pstr for c in countries) == 3
        assert sum(c in pstr for c in capitals) == 2
        pt.reset()
        # test for random and multiple prompts
        ptarr = pt.sub_from_json(
            json_path=os.path.join(self.asset_path, "capital-qa-sub.json"),
            key_to_var={"pais": ["country1", "country2", "country3"], "capitulo": ["capital1", "capital2"]},
            strategy="random",
            start_index=0,
            n=2,
        )
        assert len(ptarr) == 2
        assert isinstance(ptarr[0], PromptPattern) is True
        # test fault tolerance if n too large than what file allows
        ptarr = pt.sub_from_json(
            json_path=os.path.join(self.asset_path, "capital-qa-sub.json"),
            key_to_var={"pais": ["country1", "country2", "country3"], "capitulo": ["capital1", "capital2"]},
            strategy="sample",
            start_index=0,
            n=100,
        )
        assert len(ptarr) < 100
        assert isinstance(ptarr[0], PromptPattern) is True
        # test sequential does not return all n prompts if file is small
        ptarr = pt.sub_from_json(
            json_path=os.path.join(self.asset_path, "capital-qa-sub.json"),
            key_to_var={"pais": ["country1", "country2", "country3"], "capitulo": ["capital1", "capital2"]},
            strategy="sequential",
            start_index=0,
            n=2,
        )
        assert len(ptarr) < 2
        assert isinstance(ptarr[0], PromptPattern) is True
        # test random can return any number of prompts
        ptarr = pt.sub_from_json(
            json_path=os.path.join(self.asset_path, "capital-qa-sub.json"),
            key_to_var={"pais": ["country1", "country2", "country3"], "capitulo": ["capital1", "capital2"]},
            strategy="random",
            start_index=0,
            n=100,
        )
        assert len(ptarr) == 100
        assert isinstance(ptarr[0], PromptPattern) is True
        # test with n = -1 it returns as many prompts as it can
        ptarr = pt.sub_from_json(
            json_path=os.path.join(self.asset_path, "capital-qa-sub.json"),
            key_to_var={"pais": ["country1", "country2", "country3"], "capitulo": ["capital1", "capital2"]},
            strategy="sequential",
            start_index=0,
            n=-1,
        )
        assert len(ptarr) == 1
        assert isinstance(ptarr[0], PromptPattern) is True
        # test for start index
        ptarr = pt.sub_from_json(
            json_path=os.path.join(self.asset_path, "capital-qa-sub.json"),
            key_to_var={"pais": ["country1", "country2", "country3"], "capitulo": ["capital1", "capital2"]},
            strategy="sequential",
            start_index=1,
            n=-1,
        )
        assert len(ptarr) == 1
        assert "Estados Unidos" not in str(ptarr[0])

    def test_sub_all_from_json(self):
        with open(os.path.join(self.asset_path, "capital-qa-sub.json"), "r") as fin:
            arr = json.load(fin)
            countries = [a["pais"] for a in arr]
            capitals = [a["capitulo"] for a in arr]
        # test for sequential
        pt = PromptPattern.from_file(self.asset_path + "capital-qa-multivar.yaml")
        ptarr = pt.sub_all_from_json(
            json_path=os.path.join(self.asset_path, "capital-qa-sub.json"),
            key_to_var={"pais": ["country1", "country2", "country3"], "capitulo": ["capital1", "capital2"]},
        )
        assert len(ptarr) == 1
        assert isinstance(ptarr[0], PromptPattern) is True
        pstr = str(ptarr[0])
        assert sum(c in pstr for c in countries) == 3
        assert sum(c in pstr for c in capitals) == 2

    def test_tabular_infer_mode_helper(self):
        first_row = ["var1", "var2", "var3"]

        pt = PromptPattern.from_str("###".join(["{{" + v + "}}" for v in first_row]))
        col_to_var, columns = pt._tabular_infer_mode_helper(first_row)
        assert col_to_var == {v: [v] for v in first_row}
        assert columns == first_row

        pt = PromptPattern.from_str("First var {{0}}, then {{1}}, then {{ 2 }}")
        col_to_var, columns = pt._tabular_infer_mode_helper(first_row)
        assert col_to_var == {v: [v] for v in ["0", "1", "2"]}
        assert columns == ["0", "1", "2"]

        pt = PromptPattern.from_str("Var {{1}}, then {{2}}")
        col_to_var, columns = pt._tabular_infer_mode_helper(first_row)
        assert col_to_var == {v: [v] for v in ["1", "2"]}
        assert columns == ["0", "1", "2"]

    def test_csv_infer_mode(self):
        pt = PromptPattern.from_str("Country {{country}} capital {{capital}}")
        plist = pt.sub_all_from_csv(csv_path=os.path.join(self.asset_path, "capital-qa-sub.csv"), col_to_var="infer")
        assert len(plist) == 3
        assert str(plist[0]) == "Country USA capital Washington"
        assert str(plist[2]) == "Country China capital Beijing"

        pt = PromptPattern.from_str("Capital {{capital}} Nonexistent {{var}}")
        plist = pt.sub_all_from_csv(csv_path=os.path.join(self.asset_path, "capital-qa-sub.csv"), col_to_var="infer")
        assert len(plist) == 3
        assert str(plist[0]) == "Capital Washington Nonexistent {{var}}"
        assert str(plist[2]) == "Capital Beijing Nonexistent {{var}}"

        pt = PromptPattern.from_str("Country {{0}} capital {{1}}")
        plist = pt.sub_all_from_csv(
            csv_path=os.path.join(self.asset_path, "capital-qa-sub-noheader.csv"), col_to_var="infer", headers=False
        )
        assert len(plist) == 3
        assert str(plist[0]) == "Country USA capital Washington"
        assert str(plist[2]) == "Country China capital Beijing"

        pt = PromptPattern.from_str("Capital {{1}} Nonexistent {{15}}")
        plist = pt.sub_all_from_csv(
            csv_path=os.path.join(self.asset_path, "capital-qa-sub-noheader.csv"), col_to_var="infer", headers=False
        )
        assert len(plist) == 3
        assert str(plist[0]) == "Capital Washington Nonexistent {{15}}"
        assert str(plist[2]) == "Capital Beijing Nonexistent {{15}}"

    def test_sub_from_csv_infer_mode(self):
        pt = PromptPattern.from_str("{{col1}},{{col2}},{{col3}}")
        path = self.asset_path + "csv_file.csv"

        res = pt.sub_all_from_csv(csv_path=path, col_to_var="infer")
        assert isinstance(res, list)
        assert len(res) == 2
        assert str(res[0]) == "aa,bb,cc"
        assert str(res[1]) == "aa,bb,cc"

    def test_sub_from_csv_start_index_random_strategy(self):
        pt = PromptPattern.from_str("{{col1}},{{col2}},{{col3}}")
        path = self.asset_path + "csv_file.csv"

        with pytest.raises(Exception) as e:
            pt.sub_all_from_csv(csv_path=path, col_to_var="infer", start_index=0, strategy="random")
            assert "start_index" in str(e)

    def test_sub_from_csv_start_index_sample_strategy(self):
        pt = PromptPattern.from_str("{{col1}},{{col2}},{{col3}}")
        path = self.asset_path + "csv_file.csv"

        with pytest.raises(Exception) as e:
            pt.sub_all_from_csv(csv_path=path, col_to_var="infer", start_index=0, strategy="sample")
            assert "start_index" in str(e)
