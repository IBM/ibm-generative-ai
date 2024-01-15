"""
Shutdown Handling

To drastically improve SDKS's performance, we spawn an additional thread with its event pool (asyncio).
But because the non-main thread cannot be listening to signals like SIGINT/SIGTERM, we need the owner of the
main thread to do so; this is why we provide the 'handle_shutdown_event' function, which allows you to signalise
the termination action to the SDK.
"""
import signal

from dotenv import load_dotenv

from genai import Client, Credentials, handle_shutdown_event
from genai.text.generation import TextGenerationParameters

load_dotenv()

# If you add comments to the following lines, it will prevent the application from being canceled smoothly.
# This is because the SDK will delay the termination process until completion.
# However, by using the signal functionality, the application can be stopped almost instantly.
signal.signal(signal.SIGINT, handle_shutdown_event)
signal.signal(signal.SIGTERM, handle_shutdown_event)

credentials = Credentials.from_env()
client = Client(credentials=credentials)

try:
    responses = list(
        client.text.generation.create(
            model_id="google/flan-t5-xl",
            inputs=["Summarize human evolution from it's beginning."] * 50,
            parameters=TextGenerationParameters(min_new_tokens=100, max_new_tokens=250),
        )
    )
except InterruptedError:
    print("Generation has been aborted.")
