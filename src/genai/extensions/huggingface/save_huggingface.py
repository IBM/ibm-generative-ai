try:
    from datasets import Dataset
except ImportError:
    raise ImportError("Could not import HuggingFace Datasets: Please install ibm-generative-ai[huggingface] extension.")

from genai.prompt_pattern import PromptPattern
from genai.utils.extensions import register_promptpattern_accessor

__all__ = ["HuggingFaceDatasetExtension"]


@register_promptpattern_accessor("huggingface")
class HuggingFaceDatasetExtension:
    def __init__(self, prompt_pattern: PromptPattern):
        self._obj = prompt_pattern

    def save_dataset(self, list_of_prompts: list, path: str, key: str = "prompt"):
        """
        Given a list of prompts, creates a HuggingFace dataset in a specified path.
        Args:
            list_of_prompts (list): The list of prompts used to create the dataset from.
            path (str): Path in which you want the dataset to be saved.
            key (str, optional): Before the dataset is created, the list is converted to a dictionary.
            This parameter defines what you would like the key in the dictionary to be named.
            Defaults to "prompt".
        """

        list_of_prompts_as_dict = {key: self._obj.list_str(list_of_prompts)}
        ds = Dataset.from_dict(list_of_prompts_as_dict)
        ds.save_to_disk(path)
