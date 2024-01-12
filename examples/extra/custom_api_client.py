"""
Customize underlying API (httpx) Client
"""

from dotenv import load_dotenv

from genai import ApiClient, Client, Credentials

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint>
load_dotenv()


def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"


print(heading("Reusing API Client instance"))


credentials = Credentials.from_env()

api_client = ApiClient(
    credentials=credentials,
    config={"client_options": {"timeout": 5}},  # you can pass any 'httpx' options
)
client = Client(api_client=api_client)
