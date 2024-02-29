"""
Provide feedback to the request
"""

from dotenv import load_dotenv

from genai.client import Client
from genai.credentials import Credentials
from genai.schema import (
    RequestFeedbackCategory,
    RequestFeedbackVote,
    TextGenerationParameters,
)

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint>
load_dotenv()


def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"


client = Client(credentials=Credentials.from_env())

# Generate text
response = next(
    client.text.generation.create(
        model_id="google/flan-t5-xl",
        parameters=TextGenerationParameters(temperature=0),
        inputs=["2+3="],
    )
)
generated_text = response.results[0].generated_text.strip()
print(f"Model response: {generated_text}.")

# Send feedback based on the model response
if generated_text == "5":
    print("Correct.")
    feedback_response = client.request.feedback.create(
        request_id=response.id,
        vote=RequestFeedbackVote.UP,
        comment="Well done",
        categories=[RequestFeedbackCategory.CORRECT_STYLE, RequestFeedbackCategory.CORRECT_CONTENT],
    )
    print("Positive feedback has been sent.")
else:
    print("Incorrect.")
    feedback_response = client.request.feedback.create(
        request_id=response.id,
        vote=RequestFeedbackVote.DOWN,
        comment="Expected response was '5'",
        categories=[RequestFeedbackCategory.INACCURATE],
    )
    print("Negative feedback has been sent.")
