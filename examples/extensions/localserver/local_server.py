"""
Use a local server with a custom model

.. admonition:: Python 3.12 support
    :class: warning

    The transformers library is not supported in python 3.12 yet due to the lack of pytorch support for 3.12.
    Follow the `pytorch issue <https://github.com/pytorch/pytorch/issues/110436>`_ for more information.
"""

import logging

from genai.client import Client

# Import the ibm-generative-ai library and local server extension
from genai.extensions.localserver import LocalLLMServer, LocalModel
from genai.text.generation import (
    DecodingMethod,
    StopReason,
    TextGenerationParameters,
    TextGenerationResult,
    TextGenerationReturnOptions,
)
from genai.text.tokenization import (
    TextTokenizationCreateResults,
    TextTokenizationParameters,
)

# This example uses the transformers library, please install using:
# pip install transformers torch sentencepiece
try:
    from transformers import T5ForConditionalGeneration, T5Tokenizer
except ImportError:
    raise ImportError(
        """
Could not import transformers which is needed for this example.
Please install using: pip install transformers torch sentencepiece
"""
    )


def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"


logger = logging.getLogger(__name__)


class FlanT5Model(LocalModel):
    model_id = "google/flan-t5-base"

    def __init__(self):
        logger.info("Initialising my custom flan-t5-base model")
        self.tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-base")
        self.model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-base")
        logger.info("flan-t5-base is ready!")

    def generate(self, input_text: str, parameters: TextGenerationParameters) -> TextGenerationResult:
        logger.info(f"Calling generate on: {input_text}")
        input_ids = self.tokenizer(input_text, return_tensors="pt").input_ids
        response = self.model.generate(input_ids, max_new_tokens=parameters.max_new_tokens)

        genai_response = TextGenerationResult(
            generated_text=self.tokenizer.decode(response[0]),
            generated_token_count=response.shape[1],
            input_token_count=input_ids.shape[1],
            stop_reason=StopReason.EOS_TOKEN,
            input_text=input_text if parameters.return_options.input_text else None,
        )
        logger.info(f"Response to {input_text} was: {genai_response}")

        return genai_response

    def tokenize(self, input_text: str, parameters: TextTokenizationParameters) -> TextTokenizationCreateResults:
        logger.info(f"Calling tokenize on: {input_text}")
        tokenized = self.tokenizer(input_text).input_ids
        tokens = self.tokenizer.convert_ids_to_tokens(tokenized)
        return TextTokenizationCreateResults(
            token_count=len(tokens),
            tokens=tokens if parameters.return_tokens else None,
        )


print(heading("Use a local server with a custom model"))

# Instantiate the Local Server with your model
server = LocalLLMServer(models=[FlanT5Model])

# Start the server and execute your code
with server.run_locally():
    print(" > Server is started")
    # Instantiate a custom client
    client = Client(credentials=server.get_credentials())

    # Instantiate parameters for chat
    parameters = TextGenerationParameters(
        decoding_method=DecodingMethod.SAMPLE,
        max_new_tokens=10,
        return_options=TextGenerationReturnOptions(input_text=True),
    )

    prompts = ["Hello! How are you?", "How's the weather?"]
    for response in client.text.generation.create(model_id=FlanT5Model.model_id, inputs=prompts, parameters=parameters):
        [result] = response.results
        print(f"Prompt: {result.input_text}\nResponse: {result.generated_text}")


print(" > Server stopped, goodbye!")
