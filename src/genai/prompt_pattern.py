import copy
import csv
import random
import re
from typing import Literal, Union

import requests
from yaml import CLoader as Loader
from yaml import load

from genai.exceptions import GenAiException
from genai.utils.json_utils import json_extract, json_get_all_keys, json_load


class PromptPattern:
    _accessors = set()

    def _create(self, *args, **kwargs):
        self.url: str = None
        self.literal: bool = False
        self.dump = None
        self.yaml = None
        self.token: str = None

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.raw_content = self._fetch_prompt()

    @classmethod
    def from_url(cls, url: str, token=""):
        """
        Create a promptPattern from a resource located at a remote url.

        Args:
            url (str): Location of the resource.
            token (str, optional): User token to access the resource. Defaults to "".

        Returns:
            PromptPattern: Returns the created PromptPattern instance.
        """

        pt = PromptPattern()
        pt._create(url=url, token=token)
        return pt

    @classmethod
    def from_file(cls, path: str):
        """
        Create a promptPattern from a file.

        Args:
            path (str): Path to file.

        Returns:
            PromptPattern: Returns the created PromptPattern instance.
        """

        pt = PromptPattern()
        pt._create(url=path)
        return pt

    @classmethod
    def from_str(cls, prompt: str):
        """
        Create a promptPattern from a string.

        Args:
            prompt (str): The prompt template as string.

        Returns:
            PromptPattern: Returns the created PromptPattern instance.
        """
        pt = PromptPattern()
        pt._create(url=prompt, literal=True)
        return pt

    def _fetch_prompt(self):
        """
        Gets the raw content as a string at the path indicated by the url.
        The url can point to any http endpoint or a local path

        Returns:
            str: Contents of file located at url as a str
        """

        if not self.literal:
            if self.url.startswith("http"):
                if self.token is not None:
                    headers = {"Authorization": f"Bearer {self.token}"}
                    resp = requests.get(self.url, headers=headers)
                else:
                    resp = requests.get(self.url)
                raw_content = resp.content
                resp.close()
            else:
                with open(self.url, "r", encoding="utf-8") as file:
                    raw_content = file.read()

            self.yaml = load(raw_content, Loader=Loader)
            if "content" not in self.yaml:
                raise Exception("Invalid Prompt YAML. It must include 'content' fields.")
            self.dump = self.yaml["content"]
        else:
            raw_content = self.url
            self.dump = raw_content

        return raw_content

    def reset(self):
        if self.literal:
            self.dump = self.raw_content
        else:
            self.yaml = load(self.raw_content, Loader=Loader)
            self.dump = self.yaml["content"]

    def refetch(self):
        self.raw_content = self._fetch_prompt()

    def validate(self):
        """
        Validate if the yaml at apiVersion is correct.
        Args:
            dict: yaml
        Returns:
            returns True if passes and raises Exception otherwise
        """

        # we do not validate content of literal, so we pass as true
        if self.literal:
            return True
        if self.yaml:
            if "apiVersion" not in self.yaml:
                raise Exception("Invalid Prompt YAML. It must include 'apiVersion'.")
            if self.yaml["apiVersion"].lower() == "v0" and "content" not in self.yaml:
                raise Exception("Invalid Prompt YAML. It must include 'content' fields.")

        return True

    def find_vars(self):
        """
        Find all variables in prompt template and return in a list.

        Returns:
            list of variables in prompt template
        """

        pattern = re.compile(r"{{\s*" + "[^{}]*" + r"\s*}}")
        prompt = self.dump
        vars = re.findall(pattern, prompt)
        # remove prefix and suffix
        cleaned = []
        for var in vars:
            name = var[2:-2].strip()
            cleaned.append(name)
        return set(cleaned)

    def sub(self, var: str, value: str) -> "PromptPattern":
        """
        Substitute all variables named 'var' (indicated as {{var}} in prompt contents)

        Args:
            var: name of variable ( cannot contain the characters '{' or '}' )
            value: value to replace variable with

        Returns:
            str: contents of prompt with substitution
        """

        pattern = re.compile(r"{{\s*" + var + r"\s*}}")
        prompt = self.dump
        self.dump = re.sub(pattern, value, prompt)
        return self

    def _get_idx(self, strategy, start_index, idx, max_length, random_idx_list):
        """
        Return an index based on the given strategy

        Args:
            strategy (string): Either 'sequential', 'sample' or 'random'
            start_index (int): Start index
            idx (int): Index of element
            max_length (int): Upper bound of the return value
            random_idx_list (list[int]): List of random indexes

        Returns:
            int: The desired index
        """

        if strategy == "sequential":
            index = min(start_index + idx, max_length)
        elif strategy == "random":
            index = random.randint(0, max_length)
        elif strategy == "sample":
            index = min(start_index + idx, len(random_idx_list) - 1)
            index = random_idx_list[index]
        return index

    def sub_all_from_json(
        self,
        json_path: str,
        key_to_var: Union[dict, Literal["infer"]] = "infer",
        encoding: str = "utf-8-sig",
    ) -> list["PromptPattern"]:
        """
        Sequentially builds a list of PromptPattern from a json file. Iterates through the whole file
        from start to end.

        Args:
            json_path (str): Path to json file.
            key_to_var (dict, str): "infer" string or dict mapping of key value to list of variables.
                If "infer", the key_to_var mapping is inferred based on the template's variables' name.
                For example, assuming a variable "name" and a key "name" in the passed json file, "infer"
                is equivalent to key_to_var={"name":["name"]}. Defaults to "infer".
            encoding (str, Optional): File encoding. Defaults to "utf-8-sig".

        Returns:
            List[PromptPattern] : List of PromptPattern
        """

        strategy = "sequential"
        start_index = 0
        n = -1
        return self.sub_from_json(json_path, key_to_var, strategy, start_index, n, encoding)

    def sub_from_json(
        self,
        json_path: str,
        key_to_var: Union[dict, Literal["infer"]] = "infer",
        strategy: Literal["random", "sequential", "sample"] = "sequential",
        start_index: int = 0,
        n: int = 1,
        encoding: str = "utf-8-sig",
    ) -> Union["PromptPattern", list["PromptPattern"]]:
        """
        This will replace every variable from the key_to_var dict using data from the provided file.

        Args:
            json_path (str): Path to json or jsonl file
            key_to_var (Union[dict, Literal["infer"]]): "infer" string or dict mapping keys to variables.
                If "infer", the key_to_var mapping is inferred based on the template's variables' name.
                For example, assuming a variable "name" and a key "name" in the json file, "infer"
                is equivalent to key_to_var={"name":["name"]}. Defaults to "infer". In its most
                general form, a user can specify a mapping like key_to_var={"key": list_of_vars,. ..}
                where the list against each key is a list of variables which can be substituted from
                that key.
            strategy (Literal[sequential, sample, random], optional): Define how the template will be populated from
                the given json.
                Sequential  : sequentially subs the template's variables from the json, starting at a given start_index.
                Sample      : randomly samples rows and instantiate prompts. Without repetition of the data.
                Random      : for each prompt variable, substitute the value from the corresponding key at random
                Defaults to "sequential".
            start_index (int, optional): Only used with strategy sequential. State the first row to be used for the
                substitution in the template. Defaults to 0.
            n (int, Optional): Desired number of prompts to be returned.
                - n = 1: default, returns a PromptPattern
                - n > 1: returns a list of PromptPattern up to min(n, maximum producible prompts from file)
                - n = -1: goes through the entire file.
                If n is -1 and strategy is Random, a GenAiException is raised.
            encoding (str, Optional): File encoding. Defaults to "utf-8-sig".

        Returns:
            PromptPattern | list[PromptPattern]: A populated PromptPattern or a list of PromptPatterns
        """

        if strategy == "random" and n <= 0:
            raise GenAiException("n must be at least 1")

        with open(json_path, "r", encoding=encoding) as file:
            data = json_load(file)

            if len(data) < 1:
                raise ValueError("JSON file seems to be empty: {}".format(json_path))
            if key_to_var == "infer":
                key_to_var = self._json_infer_mode_helper(data[0])

            random_row_idx = [*range(len(data) - 1)]
            random.shuffle(random_row_idx)

            if strategy == "sample":
                start_index = 0

            PromptPattern.validate_start_index(strategy, start_index, data)

            done = False
            complete_pt = []

            while not done:
                pt = copy.copy(self)

                for key in key_to_var.keys():
                    variables = key_to_var[key]

                    for idx, val in enumerate(variables):
                        top = len(data) - 1
                        index = pt._get_idx(strategy, start_index, idx, top, random_row_idx)
                        row = data[index]
                        pt.sub(val, json_extract(row, key, join=True))

                    current_row_idx = start_index + idx
                    if (strategy == "sequential" or strategy == "sample") and current_row_idx >= len(data):
                        done = True
                        break

                if not done:
                    complete_pt.append(pt)

                if n > -1 and len(complete_pt) >= n:
                    done = True

                start_index += len(variables)

        if n == 1:
            if len(complete_pt) == 0:
                raise GenAiException("Could not produce a prompt from given parameters.")
            self.__dict__ = copy.deepcopy(complete_pt[0].__dict__)
            return self

        return complete_pt

    def sub_all_from_csv(
        self,
        csv_path: str,
        col_to_var: Union[dict, Literal["infer"]] = "infer",
        headers: bool = True,
        encoding: str = "utf-8-sig",
        delimiter: str = ",",
    ) -> list["PromptPattern"]:
        """
        Sequentially builds a list of PromptPattern from a csv file. Iterates through the whole file
        from start to end.

        Args:
            csv_path (str): Path to csv file.
            col_to_var (Union[dict, Literal["infer"]]): "infer" string or dict of column name to list of variables.
                If "infer", the col_to_var mapping is inferred based on the template's variables' name.
                For example, assuming a variable "name" and a column "name" in the passed csv file, "infer"
                is equivalent to col_to_var={"name":["name"]}. Defaults to "infer". In its most
                general form, a user can specify a mapping like col_to_var={"column": list_of_vars,. ..}
                where the list against each column is a list of variables which can be substituted from
                that column.
            headers (bool, Optional): Indicates if the csv contains a header row. Only used if inferring col_to_var.
                Defalts to True.
            encoding (str, Optional): File encoding. Defaults to "utf-8-sig".
            delimiter (str, Optional): Delimiter for the csv. Defaults to ",".

        Returns:
            List[PromptPattern] : List of PromptPattern
        """

        strategy = "sequential"
        start_index = 0
        n = -1
        return self.sub_from_csv(csv_path, col_to_var, headers, strategy, start_index, n, encoding, delimiter)

    def _json_infer_mode_helper(self, first_dict):
        vars = self.find_vars()
        if all([v.isdigit() for v in vars]):
            raise GenAiException("Variable inference with digit is not supported for JSON document.")

        keys = json_get_all_keys(first_dict)
        overlap = set(keys).intersection(vars)
        key_to_var = {v: [v] for v in overlap}
        return key_to_var

    def _tabular_infer_mode_helper(self, first_row):
        vars = self.find_vars()
        if all([v.isdigit() for v in vars]):
            columns = [str(i) for i in range(len(first_row))]
            overlap = set(columns).intersection(vars)
        else:
            columns = first_row[:]
            overlap = set(first_row).intersection(vars)

        col_to_var = {v: [v] for v in overlap}
        if col_to_var == {}:
            raise GenAiException(
                """
                Could not match variables {} to data keys {}.
                If you are inferring and using a headless csv, make sure the variables
                correspond to the index of the desired csv column.
                """.format(
                    vars, first_row
                )
            )

        return col_to_var, columns

    def _return_single_prompt_from_completed_list(self, prompts: list, n: int):
        """
        Return a single PromptTemplate is the requested number is one, changing the list of prompts as a single prompt.
        If the number of prompts is zero, raise an exception.

        Args:
            prompt (list): List of prompts to be checked.
            n (int): Number of prompts to be generated.

        Returns:
            self: If the prompt is complete.
            Raises GenAiException: If the given parameters coud not produce a prompt.
        """
        if n == 1:
            if len(prompts) == 0:
                raise GenAiException("Could not produce a prompt from given parameters.")
            self.__dict__ = copy.deepcopy(prompts[0].__dict__)
            return self

    def _random_row_idx_helper(self, data: list[list[str]]) -> list:
        """
        Returns a random row from indexes the given data.

        Args:
            data (list[list[str]]): List of rows.

        Returns:
            list[str]: A random row.
        """
        random_row_idx = [*range(len(data) - 1)]
        random.shuffle(random_row_idx)
        return random_row_idx

    def _sub_from_tabular_data(
        self,
        data: list[list[str]],
        columns: list,
        col_to_var: dict,
        start_index: int = 0,
        n: int = 1,
        strategy: Literal["random", "sequential", "sample"] = "sequential",
    ) -> list["PromptPattern"]:
        """
        Substitutes variables from a tabular data.
        Returns a complete prompt if n=1, else returns a list of prompts.

        Args:
            data (list[list[str]]): List of rows.
            columns (list): List of column names from the tabular data.
            col_to_var (dict): A dictionary mapping column names to a list of variables to substitute.
            start_index (int, Optional): Index of the row to start from. Defaults to 0.
            n (int, Optional): Number of prompts to generate. Defaults to 1.
            strategy (Literal["random", "sequential", "sample"], Optional): Strategy to use for generating prompts.
                Defaults to "sequential".

        Returns:
            list[PromptPattern]: List of PromptPattern
        """

        done = False
        complete_prompt = []
        random_row_idx = self._random_row_idx_helper(data)

        while not done:
            pt = copy.copy(self)

            for col_name in col_to_var.keys():
                col_index = columns.index(col_name)
                variables = col_to_var[col_name]

                for idx, var in enumerate(variables):
                    top = len(data) - 1
                    index = pt._get_idx(strategy, start_index, idx, top, random_row_idx)
                    row = data[index]
                    value = row[col_index]
                    pt.sub(var, str(value))

                current_row_idx = start_index + idx
                if (strategy == "sequential" or strategy == "sample") and current_row_idx >= len(data):
                    done = True
                    break

            if not done:
                complete_prompt.append(pt)

            if n > -1 and len(complete_prompt) >= n:
                done = True

            start_index += len(variables)

        return complete_prompt

    def sub_from_csv(
        self,
        csv_path: str,
        col_to_var: Union[dict, Literal["infer"]] = "infer",
        headers: bool = True,
        strategy: Literal["random", "sequential", "sample"] = "sequential",
        start_index: int = 0,
        n: int = 1,
        encoding: str = "utf-8-sig",
        delimiter: str = ",",
    ) -> Union["PromptPattern", list["PromptPattern"]]:
        """
        This will replace every variable in the col_to_var dict using data from the provided file.

        Args:
            csv_path (str): Path to csv file.
            col_to_var (Union[dict, Literal["infer"]]): "infer" string or dict of column name to list of variables.
                If "infer", the col_to_var mapping is inferred based on the template's variables' name.
                For example, assuming a variable "name" and a column "name" in csv file, "infer"
                is equivalent to col_to_var={"name":["name"]}. Defaults to "infer". In its most
                general form, a user can specify a mapping like col_to_var={"column": list_of_vars,. ..}
                where the list against each column is a list of variables which can be substituted from
                that column.
            headers (bool, Optional): Indicates if the csv contains a header row. Only used if inferring col_to_var.
                Defalts to True.
            strategy (Literal[sequential, sample, random], optional): Define how the template will be populated from
                the given csv.
                Sequential  : sequentially subs the template's variables from the json, starting at a given start_index.
                Sample      : randomly samples rows and instantiate prompts. Without repetition of the data.
                Random      : for each prompt variable, substitute the value from the corresponding key at random
                Defaults to "sequential".
            start_index (int, optional): Only used with strategy sequential. State the first row to be used for the
                substitution in the template. Defaults to 0.
            n (int, Optional): Desired number of prompts to be returned.
                - n = 1: default, returns a PromptPattern
                - n > 1: returns a list of PromptPattern up to min(n, maximum producible prompts from file)
                - n = -1: goes through the entire file.
                If n is -1 and strategy is Random, a GenAiException is raised.
            encoding (str, Optional): File encoding. Defaults to "utf-8-sig".
            delimiter (str, Optional): Delimiter for the csv. Defaults to ",".

        Returns:
            PromptPattern | list[PromptPattern]: A populated PromptPattern or a list of PromptPatterns
        """

        if strategy == "random" and n <= 0:
            raise GenAiException("n must be at least 1")

        with open(csv_path, "r", encoding=encoding) as file:
            reader = csv.reader(file, delimiter=delimiter)
            list_of_rows = list(reader)
            if len(list_of_rows) < 1:
                raise ValueError("CSV file seems to be empty: {}".format(csv_path))
            if col_to_var == "infer":
                col_to_var, columns = self._tabular_infer_mode_helper(list_of_rows[0])
                relevant_rows = list_of_rows[1:] if headers else list_of_rows
                data = [row for row in relevant_rows if len(row) >= len(columns)]
            else:
                columns = list_of_rows[0]
                data = [row for row in list_of_rows[1:] if len(row) >= len(columns)]

            if strategy == "sample":
                start_index = 0

            PromptPattern.validate_start_index(strategy, start_index, data)

            complete_pt = []
            complete_pt = self._sub_from_tabular_data(data, columns, col_to_var, start_index, n, strategy)

        # if n == 1, return a single PromptPattern
        self._return_single_prompt_from_completed_list(complete_pt, n)

        return complete_pt

    def __str__(self):
        return self.dump

    def __repr__(self):
        return self.dump

    @staticmethod
    def list_str(list_of_prompts: list["PromptPattern"]) -> list[str]:
        return [str(x) for x in list_of_prompts]

    @staticmethod
    def validate_start_index(strategy, start_index, data):
        if strategy == "sequential" and start_index >= len(data):
            raise GenAiException("start_index cannot be greater than the length of the file.")
