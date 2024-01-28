from abc import ABC, abstractmethod

from genai.schema import (
    TextGenerationParameters,
    TextGenerationResult,
    TextTokenizationCreateResults,
    TextTokenizationParameters,
)

__all__ = ["LocalModel"]


class LocalModel(ABC):
    @property
    def model_id(self):
        """Model ID
        This is the ID that you would use when defining the model you want to use

        example: "google/flan-t5-base"

        Raises:
            NotImplementedError: If you do not implement this property.
        """
        raise NotImplementedError

    @abstractmethod
    def generate(self, input_text: str, parameters: TextGenerationParameters) -> TextGenerationResult:
        """Generate a response from your llm using the provided input text and parameters

        Args:
            input_text: The input prompt chat
            parameters: The parameters that the user code wishes to be used

        Raises:
            NotImplementedError: If you do not implement this function.

        Returns:
            TextGenerationResult: The result to be sent back to the client
        """
        raise NotImplementedError

    @abstractmethod
    def tokenize(self, input_text: str, parameters: TextTokenizationParameters) -> TextTokenizationCreateResults:
        """Tokenize the input text with your model and return the output

        Args:
            input_text (str): The input prompt chat
            parameters (TextTokenizationParameters): The parameter that the user code wishes to be used

        Raises:
            NotImplementedError: If you do not implement this function.

        Returns:
            TextTokenizationCreateResults: The result to be sent back to the client
        """
        raise NotImplementedError
