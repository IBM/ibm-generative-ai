"""Reveal similarity between the source sentence and set of sentences."""

from dotenv import load_dotenv

from genai.client import Client
from genai.credentials import Credentials
from genai.schema import TextSentenceSimilarityParameters

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint>
load_dotenv()


def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"


client = Client(credentials=Credentials.from_env())

inputs = ["Hello", "world"]
model_id = "sentence-transformers/all-minilm-l6-v2"

print(heading("EXPERIMENTAL: Text Sentence Similarity"))

source_sentence = "The cat sat on the mat"
sentences = ["The cat slept on the bed", "The black cat stretched on the windowsill."]

print(f"Source sentence: {source_sentence}")
for sentence, result in zip(
    sentences,
    client.text.experimental.sentence_similarity.create(
        model_id=model_id,
        source_sentence=source_sentence,
        sentences=sentences,
        parameters=TextSentenceSimilarityParameters(truncate_input_tokens=True),
    ).results,
):
    print(f"Score: {result.score} for '{sentence}'.")
