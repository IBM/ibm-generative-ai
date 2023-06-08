import logging

# Import the ibm-generative-ai library and local server extension
from genai.extensions.localserver import CustomModel, LocalLLMServer
from genai.model import Model
from genai.schemas import GenerateParams, GenerateResult, TokenizeResult, TokenParams

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


logger = logging.getLogger(__name__)

# Create your custom model


class FlanT5Model(CustomModel):
    model_id = "google/flan-t5-base"

    def __init__(self):
        logger.info("Initialising my custom flan-t5-base model")
        self.tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-base")
        self.model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-base")
        logger.info("flan-t5-base is ready!")

    def generate(self, input_text: str, params: GenerateParams) -> GenerateResult:
        logger.info(f"Calling generate on: {input_text}")
        input_ids = self.tokenizer(input_text, return_tensors="pt").input_ids
        response = self.model.generate(input_ids, max_new_tokens=params.max_new_tokens)

        genai_response = GenerateResult(
            generated_text=self.tokenizer.decode(response[0]),
            generated_token_count=response.shape[1],
            input_token_count=input_ids.shape[1],
            stop_reason="",
        )
        logger.info(f"Response to {input_text} was: {genai_response}")

        return genai_response

    def tokenize(self, input_text: str, params: TokenParams) -> TokenizeResult:
        logger.info(f"Calling tokenize on: {input_text}")
        tokenised = self.tokenizer(input_text).input_ids
        tokens = self.tokenizer.convert_ids_to_tokens(tokenised)
        result = TokenizeResult(token_count=len(tokens))
        if params.return_tokens is True:
            result.tokens = tokens
        return result


# Instansiate the Local Server with your model
server = LocalLLMServer(models=[FlanT5Model])

# Start the server and execute your code
with server.run_locally():
    print(" > Server is started")
    # Get the credentials / connection details for the local server
    creds = server.get_credentials()

    # Instantiate parameters for text generation
    params = GenerateParams(decoding_method="sample", max_new_tokens=10)

    # Instantiate a model proxy object to send your requests
    flan_ul2 = Model(FlanT5Model.model_id, params=params, credentials=creds)

    prompts = ["Hello! How are you?", "How's the weather?"]
    for response in flan_ul2.generate_as_completed(prompts):
        print(f"Prompt: {response.input_text}\nResponse: {response.generated_text}")


print(" > Server stopped, goodbye!")
