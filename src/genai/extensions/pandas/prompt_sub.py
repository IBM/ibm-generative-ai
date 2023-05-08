from typing import Literal, Union

try:
    from pandas import DataFrame
except ImportError:
    raise ImportError("Could not import pandas: Please install ibm-generative-ai[pandas] extension.")

from genai.exceptions import GenAiException
from genai.prompt_pattern import PromptPattern
from genai.utils.extensions import register_promptpattern_accessor

__all__ = ["PandasExtension"]


@register_promptpattern_accessor("pandas")
class PandasExtension:
    def __init__(self, prompt_pattern: PromptPattern):
        self._obj = prompt_pattern

    def sub_from_dataframe(
        self,
        dataframe: DataFrame,
        col_to_var: Union[dict, Literal["infer"]] = "infer",
        headers: bool = True,
        strategy: Literal["random", "sequential", "sample"] = "sequential",
        start_index: int = 0,
        n: int = 1,  # prompt number to be returned - Optional
    ) -> Union["PromptPattern", list["PromptPattern"]]:
        """
        Substitutes variables in the prompt pattern with values from a dataframe.

        Args:
            dataframe (pandas.DataFrame): The dataframe to use for substitution.
            col_to_var (Union[dict, Literal["infer"]], Optional): "infer": String or dict of column name to list of
                variables. For example, a user can specify a mapping like col_to_var={"column": list_of_vars,. ..}
                where the list against each column is a list of variables.
                If "infer", the col_to_var mapping is inferred based on the template's variables' name.
                For example, assuming a variable "name" and a column "name" in the tabular data, "infer" is equivalent
                to col_to_var={"name":["name"]}. In its most general form, a user can specify a mapping like
                col_to_var={"column": list_of_vars,. ..} where the list against each column is a list of variables which
                can be substituted from that column. Defaults to "infer".
            headers (bool, Optional): Indicates if the dataframe contains a header row. Only used if inferring
                col_to_var. Defalts to True.
            strategy (Literal[sequential, sample, random], optional): Define how the template will be populated from
                the given json.
                Sequential  : sequentially subs the template's variables from the json, starting at a given start_index.
                Sample      : randomly samples rows and instantiate prompts. Without repetition of the data.
                Random      : for each prompt variable, substitute the value from the corresponding key at random
                Defaults to "sequential".
            start_index (int, opttional): The index to start substitution from. Only used with strategy
                sequential. State the first row to be used for the substitution in the template. Defaults to 0.
            n (int, Optional): The number of prompts to return.
                - n = 1: default, returns a PromptPattern
                - n > 1: returns a list of PromptPattern up to min(n, maximum producible prompts from file)
                - n = -1: goes through the entire file.
                If n is -1 and strategy is Random, a GenAiException is raised.

        Returns:
            PromptPattern | list[PromptPattern]: A prompt pattern or a list of prompt patterns.
        """

        if strategy == "random" and n <= 0:
            raise GenAiException("n must be at least 1")

        if len(dataframe) < 1:
            raise ValueError("Dataframe seems to be empty.")

        columns = dataframe.columns.tolist()
        data = dataframe.values.tolist()

        if col_to_var == "infer":
            col_to_var, columns = self._obj._tabular_infer_mode_helper(columns)
            data = data if headers else ([list(dataframe.columns)] + data)
        if strategy == "sample":
            start_index = 0

        self._obj.validate_start_index(strategy, start_index, data)

        complete_pt = []
        complete_pt = self._obj._sub_from_tabular_data(data, columns, col_to_var, start_index, n, strategy)

        # if n == 1, return a single PromptPattern
        self._obj._return_single_prompt_from_completed_list(complete_pt, n)

        return complete_pt

    def sub_all_from_dataframe(
        self,
        dataframe: DataFrame,
        headers: bool = True,
        col_to_var: Union[dict, Literal["infer"]] = "infer",
    ) -> list["PromptPattern"]:
        """
        Substitutes variables in the prompt pattern with values from a dataframe.

        Args:
            dataframe (pandas.DataFrame): The dataframe to use for substitution.
            headers (bool, Optional): Indicates if the dataframe contains a header row. Only used if inferring
                col_to_var. Defalts to True.
            col_to_var (Union[dict, Literal["infer"]], Optional): "infer": String or dict of column name to list of
                variables. For example, a user can specify a mapping like col_to_var={"column": list_of_vars,. ..}
                where the list against each column is a list of variables.
                If "infer", the col_to_var mapping is inferred based on the template's variables' name.
                For example, assuming a variable "name" and a column "name" in the tabular data, "infer" is equivalent
                to col_to_var={"name":["name"]}. In its most general form, a user can specify a mapping like
                col_to_var={"column": list_of_vars,. ..} where the list against each column is a list of variables which
                can be substituted from that column. Defaults to "infer".

        Returns:
            list[PromptPattern]: A list of prompt patterns.
        """
        strategy = "sequential"
        start_index = 0
        n = -1
        return self.sub_from_dataframe(dataframe, col_to_var, headers, strategy, start_index, n)
