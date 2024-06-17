"""Text Classification"""

from dotenv import load_dotenv

from genai.client import Client
from genai.credentials import Credentials
from genai.schema import TextClassificationCreateData

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint>
load_dotenv()


def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"


client = Client(credentials=Credentials.from_env())

print(heading("EXPERIMENTAL: Text Classification"))

response = client.text.experimental.classification.create(
    model_id="google/flan-t5-xl",
    input="I would like to return back the t-shirt I just bought on your e-shop.",
    data=[
        TextClassificationCreateData(text="My transfer has been declined.", labels=["declined transfer"]),
        TextClassificationCreateData(text="Can I get my money back on an item?", labels=["refund request"]),
        TextClassificationCreateData(text="How long should I wait to activate my card", labels=["activating my card"]),
    ],
)

print(f"Type: {response.result.classification_type}")
print(f"Predictions: {response.result.predictions}")
print(f"Log-Likelihood: {response.result.log_likelihood}")
print("")
print("")
print(f"MODEL INPUT\n{response.result.model_input}")
print(f"MODEL OUTPUT\n{response.result.model_output}")
