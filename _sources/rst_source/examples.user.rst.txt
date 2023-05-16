-----------------
Alice Bob QA
-----------------

..  code-block:: bash
    :caption: See `alice_bob_qa.py <https://github.ibm.com/ai-foundation/genai/blob/dev/examples/user/alice_bob_qa.py>`_ on GitHub.

    import os
    import time

    from dotenv import load_dotenv

    from genai.model import Credentials, Model
    from genai.schemas import GenerateParams, ModelType

    # make sure you have a .env file under genai root with
    # GENAI_KEY=<your-genai-key>
    load_dotenv()
    api_key = os.getenv("GENAI_KEY", None)

    print("\n------------- Example (Model QA)-------------\n")

    bob_params = GenerateParams(
        decoding_method="sample",
        max_new_tokens=25,
        min_new_tokens=1,
        stream=False,
        temperature=1,
        top_k=50,
        top_p=1,
    )

    alice_params = GenerateParams(
        decoding_method="sample",
        max_new_tokens=45,
        min_new_tokens=1,
        stream=False,
        temperature=0,
        top_k=50,
        top_p=1,
    )

    creds = Credentials(api_key)
    bob_bloomz = Model(ModelType.BLOOMZ, params=bob_params, credentials=creds)
    alice_bloomz = Model(ModelType.FLAN_T5, params=alice_params, credentials=creds)

    alice_q = "What is 1 + 1?"
    print(f"[Alice][Q] {alice_q}")

    while True:
        bob_response = bob_bloomz.generate([alice_q])
        bob_a = bob_response[0].generated_text
        print(f"[Bob][A] {bob_a}")

        bob_q = "What is " + bob_a + " + " + bob_a + "?"
        print(f"[Bob][Q] {bob_q}")

        alice_response = alice_bloomz.generate([bob_q])
        alice_a = alice_response[0].generated_text
        print(f"[Alice][A] {alice_a}")

        alice_q = "What is " + alice_a + " + " + alice_a + "?"
        print(f"[Alice][Q] {alice_q}")
        time.sleep(1)

-----------------
Alice Bob Talk
-----------------

..  code-block:: bash
    :caption: See `alice_bob_talk.py <https://github.ibm.com/ai-foundation/genai/blob/dev/examples/user/alice_bob_talk.py>`_ on GitHub.

    import os
    import time

    from dotenv import load_dotenv

    from genai.model import Credentials, Model
    from genai.schemas import GenerateParams, ModelType

    # make sure you have a .env file under genai root with
    # GENAI_KEY=<your-genai-key>
    load_dotenv()
    api_key = os.getenv("GENAI_KEY", None)

    print("\n------------- Example (Model Talk)-------------\n")

    bob_params = GenerateParams(
        decoding_method="sample",
        max_new_tokens=25,
        min_new_tokens=1,
        stream=False,
        temperature=1,
        top_k=50,
        top_p=1,
    )

    alice_params = GenerateParams(
        decoding_method="sample",
        max_new_tokens=45,
        min_new_tokens=1,
        stream=False,
        temperature=0,
        top_k=50,
        top_p=1,
    )

    creds = Credentials(api_key)
    bob_bloomz = Model(ModelType.BLOOMZ, params=bob_params, credentials=creds)
    alice_bloomz = Model(ModelType.FLAN_T5, params=alice_params, credentials=creds)

    sentence = "Hello! How are you?"
    print(f"[Alice] --> {sentence}")

    while True:
        bob_response = bob_bloomz.generate([sentence])
        # from first batch get first result generated text
        bob_gen = bob_response[0].generated_text
        print(f"[Bob] --> {bob_gen}")

        alice_response = alice_bloomz.generate([bob_gen])
        # from first batch get first result generated text
        alice_gen = alice_response[0].generated_text
        print(f"[Alice] --> {alice_gen}")

        sentence = alice_gen
        time.sleep(1)

-----------------
Async Callback
-----------------

..  code-block:: bash
    :caption: See `async_callback.py <https://github.ibm.com/ai-foundation/genai/blob/dev/examples/user/async_callback.py>`_ on GitHub.

    import os

    from dotenv import load_dotenv

    from genai.model import Credentials, Model
    from genai.schemas import GenerateParams, ModelType

    # make sure you have a .env file under genai root with
    # GENAI_KEY=<your-genai-key>
    load_dotenv()
    api_key = os.getenv("GENAI_KEY", None)

    # Using Python "with" context
    print("\n------------- Example (Greetings)-------------\n")

    # Instantiate the GENAI Proxy Object
    params = GenerateParams(
        decoding_method="sample",
        max_new_tokens=10,
        min_new_tokens=1,
        stream=False,
        temperature=0.7,
        top_k=50,
        top_p=1,
    )

    # creds object
    creds = Credentials(api_key)
    # model object
    bloomz = Model(ModelType.BLOOMZ, params=params, credentials=creds)

    greeting = "Hello! How are you?"
    lots_of_greetings = [greeting] * 1000

    # some global state for our call back
    num_of_greetings = len(lots_of_greetings)
    num_said_greetings = 0


    # called for *when* a single input is complete in generate_async and not when
    # generate returns next batch of results
    def progress_callback(result):
        global num_of_greetings
        global num_said_greetings
        num_said_greetings += 1
        print(f"[Progress {str(float(num_said_greetings/num_of_greetings)*100)}%]")
        print(f"\t {result.generated_text}")


    # yields batch of results that are produced asynchronously and in parallel
    for result in bloomz.generate_async(lots_of_greetings, progress_callback):
        pass


-----------------
Async Greetings
-----------------

..  code-block:: bash
    :caption: See `async_greetings.py <https://github.ibm.com/ai-foundation/genai/blob/dev/examples/user/async_greetings.py>`_ on GitHub.

    import os

    from dotenv import load_dotenv

    from genai.model import Credentials, Model
    from genai.schemas import GenerateParams, ModelType

    # make sure you have a .env file under genai root with
    # GENAI_KEY=<your-genai-key>
    load_dotenv()
    api_key = os.getenv("GENAI_KEY", None)

    # Using Python "with" context
    print("\n------------- Example (Greetings)-------------\n")

    # Instantiate the GENAI Proxy Object
    params = GenerateParams(
        decoding_method="sample",
        max_new_tokens=10,
        min_new_tokens=1,
        stream=False,
        temperature=0.7,
        top_k=50,
        top_p=1,
    )

    # creds object
    creds = Credentials(api_key)
    # model object
    bloomz = Model(ModelType.BLOOMZ, params=params, credentials=creds)

    greeting = "Hello! How are you?"
    lots_of_greetings = [greeting] * 1000
    num_of_greetings = len(lots_of_greetings)
    num_said_greetings = 0
    greeting1 = "Hello! How are you?"

    # yields batch of results that are produced asynchronously and in parallel
    for result in bloomz.generate_async(lots_of_greetings):
        num_said_greetings += 1
        print(f"[Progress {str(float(num_said_greetings/num_of_greetings)*100)}%]")
        print(f"\t {result.generated_text}")

-------------------
Complete My Code
-------------------

..  code-block:: bash
    :caption: See `complete_my_code.py <https://github.ibm.com/ai-foundation/genai/blob/dev/examples/user/complete_my_code.py>`_ on GitHub.

    import inspect
    import os

    from dotenv import load_dotenv

    from genai.model import Credentials, Model
    from genai.schemas import GenerateParams, ModelType

    # make sure you have a .env file under genai root with
    # GENAI_KEY=<your-genai-key>
    load_dotenv()
    api_key = os.getenv("GENAI_KEY", None)

    print("\n------------- Example (Complete my code)-------------\n")

    params = GenerateParams(
        decoding_method="sample",
        max_new_tokens=5,
        min_new_tokens=1,
        stream=False,
        temperature=0.7,
        top_k=50,
        top_p=1,
    )

    creds = Credentials(api_key)
    code_explainer = Model(ModelType.CODEGEN_MONO_16B, params=params, credentials=creds)


    # pass in an actual python function to explain
    def add_numbers(number_one, number_two):
        return number_one


    prompt = inspect.getsource(add_numbers)
    print(prompt + "\n")
    responses = code_explainer.generate([prompt])
    for response in responses:
        print(f"Generated text:\n {response.generated_text}")

-------------------
Country Capital QA
-------------------

..  code-block:: bash
    :caption: See `country-capital-qa.py <https://github.ibm.com/ai-foundation/genai/blob/dev/examples/user/country-capital-qa.py>`_ on GitHub.

    import os

    from dotenv import load_dotenv

    from genai.model import Credentials, Model
    from genai.schemas import GenerateParams, ModelType, Return

    # make sure you have a .env file under genai root with
    # GENAI_KEY=<your-genai-key>
    load_dotenv()
    api_key = os.getenv("GENAI_KEY", None)

    # Using Python "with" context
    print("\n------------- Example (Country-Capital-Factual-QA)-------------\n")

    # Instantiate the GENAI Proxy Object
    params = GenerateParams(
        decoding_method="sample",
        max_new_tokens=1,
        min_new_tokens=1,
        stream=False,
        temperature=0.7,
        top_k=50,
        top_p=1,
        return_options=ReturnOptions(input_text=False, input_tokens=True),
    )

    # creds object
    creds = Credentials(api_key)

    # model object
    bloomz = Model(ModelType.BLOOMZ, params=params, credentials=creds)

    # load a prompt from file
    with open("prompts/Country-Capital-Factual-QA", "r") as f:
        prompt = f.read()

    print(f"Prompt: \n {prompt}\n")

    # Call generate function
    responses = bloomz.generate_as_completed([prompt])
    for response in responses:
        print(f"Generated text: {response.generated_text}")

-----------------
Explain my Code
-----------------

..  code-block:: bash
    :caption: See `explain_my_code.py <https://github.ibm.com/ai-foundation/genai/blob/dev/examples/user/explain_my_code.py>`_ on GitHub.

    import inspect
    import os

    from dotenv import load_dotenv

    from genai.model import Credentials, Model
    from genai.schemas import GenerateParams, ModelType

    # make sure you have a .env file under genai root with
    # GENAI_KEY=<your-genai-key>
    load_dotenv()
    api_key = os.getenv("GENAI_KEY", None)

    print("\n------------- Example (Explain my code)-------------\n")

    params = GenerateParams(
        decoding_method="sample",
        max_new_tokens=50,
        min_new_tokens=1,
        stream=False,
        temperature=0.7,
        top_k=50,
        top_p=1,
    )

    creds = Credentials(api_key)
    code_explainer = Model(ModelType.CODEGEN_MONO_16B, params=params, credentials=creds)


    # pass in an actual python function to explain
    def add_numbers(number_one, number_two):
        return number_one + number_two


    prompt = inspect.getsource(add_numbers) + "# Explanation of what the code does"
    print(prompt + "\n")
    responses = code_explainer.generate([prompt])
    for response in responses:
        print(f"Generated text:\n {response.generated_text}")

-----------------
Many Greetings
-----------------

..  code-block:: bash
    :caption: See `many_greetings.py <https://github.ibm.com/ai-foundation/genai/blob/dev/examples/user/many_greetings.py>`_ on GitHub.

    import os

    from dotenv import load_dotenv

    from genai.model import Credentials, Model
    from genai.schemas import GenerateParams, ModelType

    # make sure you have a .env file under genai root with
    # GENAI_KEY=<your-genai-key>
    load_dotenv()
    api_key = os.getenv("GENAI_KEY", None)

    print("\n------------- Example (Greetings)-------------\n")

    params = GenerateParams(
        decoding_method="sample",
        max_new_tokens=10,
        min_new_tokens=1,
        stream=False,
        temperature=0.7,
        top_k=50,
        top_p=1,
    )

    creds = Credentials(api_key)
    bloomz = Model(ModelType.BLOOMZ, params=params, credentials=creds)

    greeting1 = "Hello! How are you?"
    greeting2 = "I am fine and you?"

    # Call generate function
    responses = bloomz.generate_as_completed([greeting1, greeting2] * 4)
    for response in responses:
        print(f"Generated text: {response.generated_text}")
