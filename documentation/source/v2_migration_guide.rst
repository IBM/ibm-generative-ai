V2 Migration Guide
==================

.. contents::
   :local:
   :class: this-will-duplicate-information-and-it-is-still-useful-here

On November 22nd, 2023, the API (v2) was announced with the following
changes.

-  New interface design that can support more modalities (code, image,
   audio) and tasks (chat, classification, transcription). We have
   worked on the interfaces together with watsonx.ai and OpenShift AI.
-  Closer alignment with `watsonx.ai<https://watsonx.ai>`_, so incubating new features in BAM
   is technically feasible.
-  Unified experience across REST API, SDKs, CLI and docs.
-  New SDK design that allows extensibility and reusability across teams
   and is more intuitive.
-  Ability to introduce minor breaking changes without affecting users.

This new design approach lets us rewrite the SDK from scratch and align
it more towards the new API. In V2, we have introduced the following
features.

-  Unify methods naming (no more ``generate``,
   ``generate_as_completed``, ``generate_async`` and so on).
-  SDK is always up-to date with the latest available API version.
-  Automatically handles concurrency and rate-limiting for all endpoints
   without any additional settings. However, one can explicitly set a
   custom concurrency limit (generate / embeddings) or batch size
   (tokenization).
-  Add implementation for every endpoint that exists on the API (generation limits, generation feedback, prompts, moderations, …).
-  Improve overall speed by re-using HTTP clients, improving concurrency
   handling and utilising API processing power.
-  Automatically generate request/output pydantic data models (data
   models are always up to date).
-  BAM API is a new default environment.

What has changed?
-----------------

- All responses that used to contain the ``results`` field of object type have gotten the field renamed to ``result``.
- ``totalCount`` param in paginated responses is renamed to ``total_count``.
- Most methods return the whole response instead of some of its subfield.
- When you see in examples dedicated classes for parameters like ``TextGenerationParameters``, you can always pass a dictionary which will be converted to the class under the hood; same applies to the enums.
- Errors are raised immediately instead of being swallowed (can be changed via an appropriate parameter).
- The ``Credentials`` class throws when an invalid endpoint is passed.
- The majority of schemas were renamed (``GenerateParams`` -> ``TextGenerationParameters``, …); for instance, if you work with text generation service (``client.text.generation.create``), all schemas can be found in ``genai.features.text.generation``, this analogy applies to every other service.
- ``tqdm`` package has been removed as we think it should not be part of the core layer. One can easily use it by wrapping the given SDK function.
- ``Model`` class has been replaced with a more general ``Client``, an entry point for all services.
- ``Options`` class has been removed, as every parameter is unpacked at the method level.


Text Generation
----------------------


How to replace ``generate``/``generate_as_completed``?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Old way:

.. code:: python

   from genai import Credentials, Model
   from genai.schemas import GenerateParams

   credentials = Credentials.from_env()
   parameters = GenerateParams(max_new_tokens=10)

   model = Model("google/flan-ul2", params=parameters, credentials=credentials)
   results = model.generate(["What is IBM?"]) # or model.generate_as_completed(["What is IBM?"])
   print(f"Generated Text: {results[0].generated_text}")

New way:

.. code:: python

   from genai import Credentials, Client
   from genai.text.generation import TextGenerationParameters

   credentials = Credentials.from_env()
   parameters = TextGenerationParameters(max_new_tokens=10)

   client = Client(credentials=credentials)
   responses = list(client.text.generation.create(model_id="google/flan-ul2", inputs=["What is IBM?"]))
   print(f"Generated Text: {responses[0].results[0].generated_text}")

You can see that the newer way is more typing, but you can retrieve
top-level information like: ``id``, ``created_at``, …

Streaming
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Old way:

.. code:: python

   from genai import Credentials, Model
   from genai.schemas import GenerateParams

   credentials = Credentials.from_env()
   parameters = GenerateParams(streaming=True, max_new_tokens=30)

   model = Model("google/flan-ul2", params=parameters, credentials=credentials)
   for response in model.generate(["What is IBM?"], raw_response=True):
       print(response)

New way:

.. code:: python

   from genai import Credentials, Client
   from genai.text.generation import TextGenerationParameters

   credentials = Credentials.from_env()
   parameters = TextGenerationParameters(max_new_tokens=30)

   client = Client(credentials=credentials)
   for response in client.text.generation.create_stream(model_id="google/flan-ul2", input="What is IBM?"):
       print(response)

Notes

- ``stream`` parameter is replaced by using method ``create_stream``.


How to replace ``generate_async``?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The old ``generate_async`` method has worked by sending multiple requests asynchronously (it spawns a new thread and runs an event loop). This is now a default behaviour for the ``create`` method in ``GenerationService`` (``client.text.generation.create``).

.. code:: python

   from tqdm.auto import tqdm
   from genai import Client, Credentials

   credentials = Credentials.from_env()
   client = Client(credentials=credentials)
   prompts = ["Prompt A", "Prompt B", "..."]

   for response in tqdm(
       total=len(prompts),
       desc="Progress",
       unit=" inputs",
       iterable=client.text.generation.create(
           model_id="google/flan-ul2",
           inputs=prompts
       )
   ):
       print(f"Response ID: {response.id}")
       print(response.results)

Notes

-  ``max_concurrency_limit``/``callback`` parameters are now located
   under ``execution_options`` parameter.

-  ``options`` parameter has been removed; every possible request
   parameter is now being parameter of the function; for instance: in
   previous version ``prompt_id`` had to be part of ``options``
   parameter, now ``prompt_id`` is a standalone function parameter.

-  results are now automatically in-order (``ordered=True``), old
   behaviour was ``ordered=False``/

-  ``throw_on_error`` is by default set to ``True`` (old behaviour -
   set to ``False`` by default). In case of ``True``, you will never
   receive a ``None`` as a response.

-  ``return_raw_response`` parameter was removed, the raw response is
   now returned automatically (this is why you need to write
   ``response.results[0].generated_text`` instead of
   ``response.generated_text``; although it may seem more complex it’s
   more robust because you will never lose any information contained at
   the top-level).

-  ``tqdm`` progressbar together with ``hide_progressbar`` property has
   been removed; you now have to use ``tqdm`` in your own (see example
   above).

Tokenization
------------

Similarly to ``generation`` related unification; ``tokenization``
service provides a single ``create`` method, which does the heavy lifting
for you. With the new API, we have decided to remove constraints on the input
items length; however, HTTP payload size and rate limiting are still
there and new SDK takes care of it by ensuring that input items are
dynamically chunked based on their byte size and by user-provided limit
(if provided). So it’s up to you if you have any limitations on the input
size.


How to replace ``tokenize`` / ``tokenize_as_completed`` / ``tokenize_async``?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Old way:

.. code:: python

   from genai import Credentials, Model
   from genai.schemas import GenerateParams

   credentials = Credentials.from_env()
   model = Model("google/flan-ul2", params=GenerateParams(max_new_tokens=20), credentials=credentials)
   prompts = ["What is IBM?"] * 100

   for response in model.tokenize_async(prompts, return_tokens=True, ordered=True):
       print(response.results)

New way:

.. code:: python

   from genai import Client, Credentials
   from genai.text.tokenization import TextTokenizationParameters, CreateExecutionOptions, TextTokenizationReturnOptions

   credentials = Credentials.from_env()
   client = Client(credentials=credentials)
   prompts = ["What is IBM?"] * 100

   for response in client.text.tokenization.create(
       model_id="google/flan-ul2",
       input=prompts,
       parameters=TextTokenizationParameters(
          return_options=TextTokenizationReturnOptions(
                tokens=True,  # return tokens
          )
       ),
       execution_options=CreateExecutionOptions(
          ordered=True,
          batch_size=5,  # (optional) every HTTP request will contain maximally requests,
          concurrency_limit=10,  # (optional) maximally 10 requests wil run at the same time
       ),
   ):
       print(response.results)

Notes

-  results are now ordered by default
-  ``throw_on_error`` is by default set to ``True`` (old behaviour - set to ``False`` by default).In case of ``True``, you will never receive a ``None`` as a response.
-  ``return_tokens``/``callbacks`` parameter is now located under ``parameters``.
-  ``client.text.tokenization.create`` returns a ``generator`` instead of ``list``, to work with it as a list, just do ``responses = list(client.text.tokenization.create(...))``.
-  ``stop_reason`` enums are changing from ``SCREAMING_SNAKE_CASE`` to ``snake_case`` (e.g. ``MAX_TOKENS`` -> ``max_tokens``), you can use the prepared ``StopReason`` enum.

Models
------

Old way

.. code:: python

   from genai import Model, Credentials

   credentials = Credentials.from_env()
   all_models = Model.list(credentials=credentials)

   model = Model("google/flan-ul2", credentials=credentials)
   detail = model.info() # get info about current model
   is_available = model.available() # check if model exists

New way:

.. code:: python

   from genai import Client, Credentials

   credentials = Credentials.from_env()
   client = Client(credentials=credentials)

   all_models = client.model.list(offset=0, limit=100) # parameters are optional
   detail = client.model.retrieve("google/flan-ul2")
   is_available = True # model exists otherwise previous line would throw an exception

Notes

-  Client throws an exception when a model does not exist instead of returning ``None``.
-  Client always returns the whole response instead of the response results.
-  Pagination has been added.

Files
-----

Old way

.. code:: python

   from genai import Model, Credentials
   from genai.services import FileManager
   from genai.schemas import FileListParams

   credentials = Credentials.from_env()

   file_list = FileManager.list_files(credentials=credentials, params=FileListParams(offset=0, limit=5))
   file_metadata = FileManager.file_metadata(credentials=credentials, file_id="id")
   file_content = FileManager.read_file(credentials=credentials, file_id="id")
   uploaded_file = FileManager.upload_file(credentials=credentials, file_path="path_on_your_system", purpose="tune")
   FileManager.delete_file(credentials=credentials, file_id="id")

New way:

.. code:: python

   from genai import Client, Credentials
   from genai.file import FilePurpose

   credentials = Credentials.from_env()
   client = Client(credentials=credentials)

   file_list = client.file.list(offset=0, limit=5) # you can pass way more filters
   file_metadata = client.file.retrieve("id")
   file_content = client.file.read("id")
   uploaded_file = client.file.create(file_path="path_on_your_system", purpose=FilePurpose.TUNE) # or just purpose="tune"
   client.file.delete(credentials=credentials, file_id="id")


Tunes
-----

Old way

.. code:: python

   from genai import Model, Credentials
   from genai.services import TuneManager
   from genai.schemas.tunes_params import (
       CreateTuneHyperParams,
       CreateTuneParams,
       DownloadAssetsParams,
       TunesListParams,
   )

   credentials = Credentials.from_env()

   tune_list = TuneManager.list_tunes(credentials=credentials, params=TunesListParams(offset=0, limit=5))
   tune_methods = TuneManager.get_tune_methods(credentials=credentials)
   tune_detail = TuneManager.get_tune(credentials=credentials, tune_id="id")
   tune_content = TuneManager.download_tune_assets(credentials=credentials, params=DownloadAssetsParams(id="tune_id", content="encoder"))
   upload_tune = TuneManager.create_tune(credentials=credentials, params=CreateTuneParams(model_id="google/flan-ul2", task_id="generation", name="my tuned model", method_id="pt", parameters=CreateTuneHyperParams(...)))
   TuneManager.delete_tune(credentials=credentials, tune_id="id")

   # or via `Model` class

   model =  Model("google/flan-ul2", params=None, credentials=credentials)
   tuned_model = model.tune(
       name="my tuned model",
       method="pt",
       task="generation",
       hyperparameters=CreateTuneHyperParams(...)
   )
   tuned_model.download(...)
   tuned_model.info(...)
   tuned_model.delete(...)

New way:

.. code:: python

   from genai import Client, Credentials
   from genai.tune import TuneStatus, TuningType, TuneAssetType

   credentials = Credentials.from_env()
   client = Client(credentials=credentials)

   tune_list = client.tune.list(offset=0, limit=5, status=TuneStatus.COMPLETED) # or just status="completed"
   tune_methods = client.tune.types()
   tune_detail = client.tune.retrieve("tune_id")
   tune_content = client.tune.read(id="tune_id", type=TuneAssetType.LOGS) # or type="logs"
   upload_tune = client.tune.create(name="my tuned model", model_id="google/flan-ul2", task_id="generation", tuning_type=TuningType.PROMPT_TUNING) # tuning_type="prompt_tuning"
   client.tune.delete("tune_id")

Notes

- ``task`` is now ``task_id``
- ``method_id`` is now ``tuning_type``, the list of allowable values has changed (use ``TuningType`` enum or values from the documentation; accepted values are changing from ``pt`` and ``mpt`` to ``prompt_tuning`` and ``multitask_prompt_tuning``).
- ``init_method`` enums are changing from ``SCREAMING_SNAKE_CASE`` to ``snake_case`` (e.g. ``RANDOM`` -> ``random``)
- ``status`` enums are changing from ``SCREAMING_SNAKE_CASE`` to ``snake_case`` (e.g. ``COMPLETED`` -> ``completed``), you can use the prepared ``TuneStatus`` enum.

Prompt Template (Prompt Pattern)
--------------------------------

The ``PromptPattern`` class has been removed as it was a local
duplication of the API’s Prompt Templates (Prompts). Prompt Templates
have been replaced by the more general ``Prompts``.

See the following example if you want to create a reusable prompt
(prompt with a template).

.. code:: python

   from genai import Client, Credentials

   client = Client(credentials=Credentials.from_env())

   # Create prompt
   prompt_response = client.prompt.create(
       model_id="google/flan-ul2",
       name="greet prompt",
       input="Hello {{name}}, enjoy your flight to {{destination}}!",
       data={"name": "Mr./Mrs.", "destination": "Unknown"}, # optional
   )
   prompt_id = prompt_response.result.id

   # Render prompt via text generation endpoint
   generate_response = client.text.generation.create(
       prompt_id=prompt_id,
       data={
           "name": "Alex",
           "destination": "London"
       }
   )

   # Response: Hello Alex, enjoy your flight to London!
   print(f"Response: {next(generate_response).results[0].generated_text}")

History (Requests History)
--------------------------

Old way

.. code:: python

   from genai.credentials import Credentials
   from genai.metadata import Metadata
   from genai.schemas.history_params import HistoryParams


   metadata = Metadata(Credentials.from_env())
   params = HistoryParams(
       limit=8,
       offset=0,
       status="SUCCESS",
       origin="API",
   )

   history_response = metadata.get_history(params)

New way:

.. code:: python

   from genai import Client, Credentials
   from genai.request import RequestStatus, RequestRetrieveOriginParameter

   client = Client(credentials=Credentials.from_env())

   history_response = client.request.list(
       limit=8,
       offset=0,
       status=RequestStatus.SUCCESS,  # or status="success"
       origin=RequestRetrieveOriginParameter.API,  # or origin="api"
   )

Notes

- ``status``, ``origin`` and endpoint ``enums`` are changing from ``SCREAMING_SNAKE_CASE`` to ``snake_case`` (e.g. ``SUCCESS`` -> ``success``). Feel free to use prepared Python enums.
- By default, all origins are now returned (as opposed to generate only in v1).
- Response object now includes ``version`` field describing major and minor version of API used when the request was created.
- Requests made under v1 as well as v2 are returned (while v1/requests endpoint returns only v1 requests).


Extensions
--------------------------

Notes

- ``PandasExtension`` was removed, because the functionality was replaced by API's prompt templates.
- Third party extensions were updated to work with latest versions of the libraries
- If you were using local models through a ``LocalLLMServer``, you may need to adjust them to the new parameter and return types.
