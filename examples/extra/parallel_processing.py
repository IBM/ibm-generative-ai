"""
Text generation with custom concurrency limit and multiple processes

The following example depicts how to limit concurrency to be able to process outputs from multiple models at once.
Such a technique is necessary to prevent spending all resources in the first instance.
"""

from multiprocessing import Pool


def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"


def run(model_id: str, limit: int):
    from dotenv import load_dotenv

    from genai import Client, Credentials
    from genai.schema import TextGenerationParameters
    from genai.text.generation import CreateExecutionOptions

    # make sure you have a .env file under genai root with
    # GENAI_KEY=<your-genai-key>
    # GENAI_API=<genai-api-endpoint>
    load_dotenv()

    client = Client(credentials=Credentials.from_env())

    for response in client.text.generation.create(
        model_id=model_id,
        inputs=["What is a molecule?"] * 20,
        execution_options=CreateExecutionOptions(concurrency_limit=limit, ordered=False),
        parameters=TextGenerationParameters(min_new_tokens=10, max_new_tokens=25),
    ):
        print(f"[{model_id}] Generated Text: {response.results[0].generated_text}")


if __name__ == "__main__":
    parameters = [("google/flan-ul2", 3), ("google/flan-t5-xl", 5), ("google/flan-t5-xxl", 2)]
    print(heading(f"Run text generation in {len(parameters)} processes"))

    with Pool(processes=len(parameters)) as pool:
        pool.starmap(run, parameters)
