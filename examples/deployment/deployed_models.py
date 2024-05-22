"""
Get all deployed models
"""

from pprint import pprint

from dotenv import load_dotenv

from genai.client import Client
from genai.credentials import Credentials

load_dotenv()


def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"


# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint> (optional) DEFAULT_API = "https://bam-api.res.ibm.com"
client = Client(credentials=Credentials.from_env())

print(heading("Get list of deployed models"))
deployment_list = client.deployment.list()
for deployment in deployment_list.results:
    pprint(deployment.model_dump())

if len(deployment_list.results) < 1:
    print("No deployed models found.")
    exit(1)

print(heading("Retrieve information about first deployment"))
deployment_info = client.deployment.retrieve(id=deployment_list.results[0].id)
pprint(deployment_info.model_dump())
