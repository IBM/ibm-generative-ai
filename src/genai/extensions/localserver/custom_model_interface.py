from abc import ABC, abstractmethod

from genai.schemas import GenerateParams, GenerateResult, TokenizeResult, TokenParams


class CustomModel(ABC):
    @property
    def model_id(self):
        """Model ID
        This is the ID that you would use when defining the model you want to use in genai

        example: "google/flan-t5-base"

        Raises:
            NotImplementedError: If you do not implement this property.
        """
        raise NotImplementedError

    @abstractmethod
    def generate(self, input_text: str, params: GenerateParams) -> GenerateResult:
        """Generate a response from your llm using the provided input text and parameters

        Args:
            input_text (str): The input prompt text
            params (GenerateParams): The parameters that the user code wishes to be used

        Raises:
            NotImplementedError: If you do not implement this function.

        Returns:
            GenerateResult: The result to be sent back to the client
        """
        raise NotImplementedError

    @abstractmethod
    def tokenize(self, input_text: str, params: TokenParams) -> TokenizeResult:
        """Tokenize the input text with your model and return the output

        Args:
            input_text (str): The input prompt text
            params (TokenParams): The parametersthat the user code wishes to be used

        Raises:
            NotImplementedError: If you do not implement this function.

        Returns:
            TokenizeResult: The result to be sent back to the client
        """
        raise NotImplementedError
