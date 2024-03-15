"""
Error Handling

How to handle SDK exceptions.
"""

from genai import Client, Credentials
from genai.exceptions import ApiNetworkException, ApiResponseException, ValidationError
from genai.schema import TextGenerationParameters

credentials = Credentials.from_env()
client = Client(credentials=credentials)

try:
    response = client.text.generation.create(
        model_id="non-existing-model",
        inputs=["Hello world!"],
        parameters=TextGenerationParameters(temperature=1, max_new_tokens=50),
    )
    print(response)
except ApiResponseException as e:
    print(e.message)  # our handcrafted message
    print(e.response.model_dump_json())  # parsed error response from the API
    # {
    #     "status_code": 404,
    #     "error": "Not Found",
    #     "message": "Model not found",
    #     "extensions": {
    #         "code": "NOT_FOUND",
    #         "state": {
    #             "model_id": "non-existing-model"
    #         }
    #     }
    # }
except ApiNetworkException as e:
    print("The server could not be reached")
    print(e.__cause__)  # an underlying exception from 'httpx' library
except ValidationError as e:
    print("Provided parameters are not valid")
    print(e)
