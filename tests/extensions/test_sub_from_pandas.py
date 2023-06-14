import pathlib

import pytest


@pytest.mark.extension
class TestPandasExtension:
    def setup_method(self):
        self.path = pathlib.Path(__file__).parent.resolve()
        self.asset_path = pathlib.Path(__file__, "..", "..", "assets").resolve()

    def test_sub_from_dataframe_random(self):
        import pandas as pd

        import genai.extensions.pandas  # noqa
        from genai.prompt_pattern import PromptPattern

        pt = PromptPattern.from_file(str(self.asset_path / "csv_file.yaml"))

        path = self.asset_path / "csv_file.csv"
        df = pd.read_csv(path)

        pt.pandas.sub_from_dataframe(
            dataframe=df,
            strategy="random",
            col_to_var={
                "col1": ["v1", "v2"],
                "col2": ["v4"],
                "col3": ["v3"],
            },
        )
        assert str(pt).replace("\n", "") == "aa,aa,cc,bb,"

    def test_sub_from_dataframe_start_index_random_strategy(self):
        import pandas as pd

        import genai.extensions.pandas  # noqa
        from genai.prompt_pattern import PromptPattern

        pt = PromptPattern.from_str("{{col1}},{{col2}},{{col3}}")
        path = self.asset_path / "csv_file.csv"
        df = pd.read_csv(path)

        with pytest.raises(Exception) as e:
            pt.pandas.sub_all_from_dataframe(dataframe=df, col_to_var="infer", start_index=0, strategy="random")
            assert "start_index" in str(e)

    def test_sub_from_dataframe_start_index_sample_strategy(self):
        import pandas as pd

        import genai.extensions.pandas  # noqa
        from genai.prompt_pattern import PromptPattern

        pt = PromptPattern.from_str("{{col1}},{{col2}},{{col3}}")
        path = self.asset_path / "csv_file.csv"
        df = pd.read_csv(path)

        with pytest.raises(Exception) as e:
            pt.pandas.sub_all_from_dataframe(dataframe=df, col_to_var="infer", start_index=0, strategy="sample")
            assert "start_index" in str(e)

    def test_sub_from_dataframe_random_row(self):
        import pandas as pd

        import genai.extensions.pandas  # noqa
        from genai.prompt_pattern import PromptPattern

        pt = PromptPattern.from_file(str(self.asset_path / "csv_file.yaml"))

        path = self.asset_path / "csv_file.csv"
        df = pd.read_csv(path)

        pt.pandas.sub_from_dataframe(dataframe=df, col_to_var={"col1": ["v2"]})
        assert str(pt).replace("\n", "") == "{{v1}},aa,{{v3}},{{v4}},"

    def test_sub_from_dataframe_infer_mode(self):
        import pandas as pd

        import genai.extensions.pandas  # noqa
        from genai.prompt_pattern import PromptPattern

        pt = PromptPattern.from_str("{{col1}},{{col2}},{{col3}}")
        path = self.asset_path / "csv_file.csv"
        df = pd.read_csv(path)

        res = pt.pandas.sub_all_from_dataframe(dataframe=df, col_to_var="infer")
        assert isinstance(res, list)
        assert len(res) == 2
        assert str(res[0]) == "aa,bb,cc"
        assert str(res[1]) == "aa,bb,cc"

    def test_sub_all_from_dataframe_infer_mode(self):
        import pandas as pd

        import genai.extensions.pandas  # noqa
        from genai.prompt_pattern import PromptPattern

        pt = PromptPattern.from_str("Country {{country}} capital {{capital}}")
        path = self.asset_path / "capital-qa-sub.csv"
        df = pd.read_csv(path)

        plist = pt.pandas.sub_all_from_dataframe(dataframe=df, col_to_var="infer")
        assert len(plist) == 3
        assert str(plist[0]) == "Country USA capital Washington"
        assert str(plist[2]) == "Country China capital Beijing"

    def test_sub_all_from_dataframe_nonexistent_var_infer_mode(self):
        import pandas as pd

        import genai.extensions.pandas  # noqa
        from genai.prompt_pattern import PromptPattern

        pt = PromptPattern.from_str("Capital {{capital}} Nonexistent {{var}}")
        path = self.asset_path / "capital-qa-sub.csv"
        df = pd.read_csv(path)

        plist = pt.pandas.sub_all_from_dataframe(dataframe=df, col_to_var="infer")
        assert len(plist) == 3
        assert str(plist[0]) == "Capital Washington Nonexistent {{var}}"
        assert str(plist[2]) == "Capital Beijing Nonexistent {{var}}"

    def test_sub_all_from_dataframe_with_no_header(self):
        import pandas as pd

        import genai.extensions.pandas  # noqa
        from genai.prompt_pattern import PromptPattern

        pt = PromptPattern.from_str("Country {{0}} capital {{1}}")
        path = self.asset_path / "capital-qa-sub-noheader.csv"

        df_no_header = pd.read_csv(path, header=None)
        plist = pt.pandas.sub_all_from_dataframe(dataframe=df_no_header, col_to_var="infer")
        assert len(plist) == 3
        assert str(plist[0]) == "Country USA capital Washington"
        assert str(plist[2]) == "Country China capital Beijing"

        df = pd.read_csv(path)
        plist = pt.pandas.sub_all_from_dataframe(dataframe=df, col_to_var="infer", headers=False)
        assert len(plist) == 3
        assert str(plist[0]) == "Country USA capital Washington"
        assert str(plist[2]) == "Country China capital Beijing"

    def test_infer_mode_col_to_var_empty(self):
        import pandas as pd

        import genai.extensions.pandas  # noqa
        from genai.prompt_pattern import PromptPattern

        pt = PromptPattern.from_str("{{animal}},{{specices}},{{island}},{{something}},{{year}}")
        path = self.asset_path / "penguins.csv"
        with pytest.raises(Exception) as e:
            df = pd.read_csv(path, index_col=0, header=None)
            pt.pandas.sub_all_from_dataframe(dataframe=df, col_to_var="infer", headers=False)
            assert "col_to_var" in str(e)
