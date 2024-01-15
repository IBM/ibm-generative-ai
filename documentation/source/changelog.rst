Changelog
=========


(unreleased)
------------

📖 Docs
^^^^^^
- docs: add changelog [`@jezekra1 <https://github.com/jezekra1>`_]
- docs: update badges [`@Tomas2D <https://github.com/Tomas2D>`_]

**Full Changelog**: `v2.0.0...HEAD <https://github.com/IBM/ibm-generative-ai/compare/v2.0.0...HEAD>`_


🔗 API Endpoint Versions
^^^^^^^^^^^^^^^^^^^^^^^^

.. collapse:: API Endpoint Versions

    ========  ==================================  ======================
    Method    Path                                Version (YYYY-MM-DD)
    ========  ==================================  ======================
    GET       /v2/api_key                         2023-11-22
    POST      /v2/api_key/regenerate              2023-11-22
    GET       /v2/files                           2023-12-15
    POST      /v2/files                           2023-12-15
    DELETE    /v2/files/{id}                      2023-11-22
    GET       /v2/files/{id}                      2023-12-15
    GET       /v2/files/{id}/content              2023-11-22
    GET       /v2/models                          2023-11-22
    GET       /v2/models/{id}                     2024-01-10
    GET       /v2/prompts                         2024-01-10
    POST      /v2/prompts                         2024-01-10
    DELETE    /v2/prompts/{id}                    2023-11-22
    GET       /v2/prompts/{id}                    2024-01-10
    PATCH     /v2/prompts/{id}                    2024-01-10
    PUT       /v2/prompts/{id}                    2024-01-10
    GET       /v2/requests                        2023-11-22
    DELETE    /v2/requests/chat/{conversationId}  2023-11-22
    GET       /v2/requests/chat/{conversationId}  2023-11-22
    DELETE    /v2/requests/{id}                   2023-11-22
    GET       /v2/tasks                           2023-11-22
    POST      /v2/text/chat                       2024-01-10
    POST      /v2/text/chat/output                2024-01-10
    POST      /v2/text/chat_stream                2024-01-10
    POST      /v2/text/embeddings                 2023-11-22
    GET       /v2/text/embeddings/limits          2023-11-22
    GET       /v2/text/extraction/limits          2023-11-22
    POST      /v2/text/generation                 2024-01-10
    POST      /v2/text/generation/comparison      2023-11-22
    GET       /v2/text/generation/limits          2023-11-22
    POST      /v2/text/generation/output          2023-11-22
    GET       /v2/text/generation/{id}/feedback   2023-11-22
    POST      /v2/text/generation/{id}/feedback   2023-11-22
    PUT       /v2/text/generation/{id}/feedback   2023-11-22
    POST      /v2/text/generation_stream          2024-01-10
    POST      /v2/text/moderations                2023-11-22
    POST      /v2/text/tokenization               2024-01-10
    GET       /v2/tunes                           2023-11-22
    POST      /v2/tunes                           2023-11-22
    POST      /v2/tunes/import                    2023-11-22
    DELETE    /v2/tunes/{id}                      2023-11-22
    GET       /v2/tunes/{id}                      2023-11-22
    PATCH     /v2/tunes/{id}                      2023-11-22
    GET       /v2/tunes/{id}/content/{type}       2023-12-15
    GET       /v2/tuning_types                    2023-11-22
    DELETE    /v2/user                            2023-11-22
    GET       /v2/user                            2023-11-22
    PATCH     /v2/user                            2023-11-22
    POST      /v2/user                            2023-11-22
    ========  ==================================  ======================

v2.0.0 (2024-01-15)
-------------------

On November 22nd, 2023, the API (v2) was announced. We reflected this change on the Python SDK by rewriting its core to be faster, more reliable and mainly in sync with the API. The new SDK brings the concept of the central client, which gives you access to the API very straightforward. This concept was recently integrated into OpenAI SDK / Cohere SDK, and more are joining.

To seamlessly migrate from V0.X versions to 2.0, we have prepared the Migration Guide. The reborn documentation with a lot of examples will help you get started.

Here is a little sneak peek.


* Very Performant.
* Generated Typings directly from the API.
* Smart Requests Concurrency Handling.
* Retry Mechanism in case of network or API failure.
* Batching Large Requests automatically.
* Easy to extend.

**Full Changelog**: `v0.6.1...v2.0.0 <https://github.com/IBM/ibm-generative-ai/compare/v0.6.1...v2.0.0>`_

🔗 API Endpoint Versions
^^^^^^^^^^^^^^^^^^^^^^^^

.. collapse:: API Endpoint Versions

    ========  ==================================  ======================
    Method    Path                                Version (YYYY-MM-DD)
    ========  ==================================  ======================
    GET       /v2/api_key                         2023-11-22
    POST      /v2/api_key/regenerate              2023-11-22
    GET       /v2/files                           2023-12-15
    POST      /v2/files                           2023-12-15
    DELETE    /v2/files/{id}                      2023-11-22
    GET       /v2/files/{id}                      2023-12-15
    GET       /v2/files/{id}/content              2023-11-22
    GET       /v2/models                          2023-11-22
    GET       /v2/models/{id}                     2024-01-10
    GET       /v2/prompts                         2024-01-10
    POST      /v2/prompts                         2024-01-10
    DELETE    /v2/prompts/{id}                    2023-11-22
    GET       /v2/prompts/{id}                    2024-01-10
    PATCH     /v2/prompts/{id}                    2024-01-10
    PUT       /v2/prompts/{id}                    2024-01-10
    GET       /v2/requests                        2023-11-22
    DELETE    /v2/requests/chat/{conversationId}  2023-11-22
    GET       /v2/requests/chat/{conversationId}  2023-11-22
    DELETE    /v2/requests/{id}                   2023-11-22
    GET       /v2/tasks                           2023-11-22
    POST      /v2/text/chat                       2024-01-10
    POST      /v2/text/chat/output                2024-01-10
    POST      /v2/text/chat_stream                2024-01-10
    POST      /v2/text/embeddings                 2023-11-22
    GET       /v2/text/embeddings/limits          2023-11-22
    GET       /v2/text/extraction/limits          2023-11-22
    POST      /v2/text/generation                 2024-01-10
    POST      /v2/text/generation/comparison      2023-11-22
    GET       /v2/text/generation/limits          2023-11-22
    POST      /v2/text/generation/output          2023-11-22
    GET       /v2/text/generation/{id}/feedback   2023-11-22
    POST      /v2/text/generation/{id}/feedback   2023-11-22
    PUT       /v2/text/generation/{id}/feedback   2023-11-22
    POST      /v2/text/generation_stream          2024-01-10
    POST      /v2/text/moderations                2023-11-22
    POST      /v2/text/tokenization               2024-01-10
    GET       /v2/tunes                           2023-11-22
    POST      /v2/tunes                           2023-11-22
    POST      /v2/tunes/import                    2023-11-22
    DELETE    /v2/tunes/{id}                      2023-11-22
    GET       /v2/tunes/{id}                      2023-11-22
    PATCH     /v2/tunes/{id}                      2023-11-22
    GET       /v2/tunes/{id}/content/{type}       2023-12-15
    GET       /v2/tuning_types                    2023-11-22
    DELETE    /v2/user                            2023-11-22
    GET       /v2/user                            2023-11-22
    PATCH     /v2/user                            2023-11-22
    POST      /v2/user                            2023-11-22
    ========  ==================================  ======================


v0.6.1 (2023-12-20)
-------------------


* fix: correct llama-index import for new version by @David-Kristek in `#243 <https://github.com/IBM/ibm-generative-ai/pull/243>`_
* fix(examples): correct Hugging Face example prompt by @David-Kristek in `#244 <https://github.com/IBM/ibm-generative-ai/pull/244>`_
* fix: prevent duplicating template with same name by @Tomas2D in `#245 <https://github.com/IBM/ibm-generative-ai/pull/245>`_

**Full Changelog**: `v0.6.0...v0.6.1 <https://github.com/IBM/ibm-generative-ai/compare/v0.6.0...v0.6.1>`_


v0.6.0 (2023-12-08)
-------------------


* feat(extensions): add support for llamaindex by @David-Kristek in `#238 <https://github.com/IBM/ibm-generative-ai/pull/238>`_
* fix: update aiohttp to support python 3.12 by @Tomas2D in `#239 <https://github.com/IBM/ibm-generative-ai/pull/239>`_
* fix: add missing **init**.py in package to fix broken import by @jezekra1 in `#241 <https://github.com/IBM/ibm-generative-ai/pull/241>`_
* fix: update maximal local concurrency limit based on API response by @Tomas2D in `#242 <https://github.com/IBM/ibm-generative-ai/pull/242>`_

New Contributors
^^^^^^^^^^^^^^^^


* @jezekra1 made their first contribution in `#241 <https://github.com/IBM/ibm-generative-ai/pull/241>`_

**Full Changelog**: `v0.5.1...v0.5.2 <https://github.com/IBM/ibm-generative-ai/compare/v0.5.1...v0.5.2>`_


v0.5.1 (2023-11-17)
-------------------

🐛 Bug fixes
^^^^^^^^^^^^


* Add missing rate-limit check for tokenize methods
* Unify error messages between sync and async methods

**Full Changelog**: `v0.5.0...v0.5.1 <https://github.com/IBM/ibm-generative-ai/compare/v0.5.0...v0.5.1>`_


v0.5.0 (2023-11-13)
-------------------

🚀 Features / Enhancements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


* Added integration for LangChain Chat Models; see an example of `generation <https://github.com/IBM/ibm-generative-ai/blob/main/examples/user/langchain_chat_generate.py>`_ and `streaming <https://github.com/IBM/ibm-generative-ai/blob/main/examples/user/langchain_chat_stream.py>`_.
* Added support for LangChain Model Serialization (saving and loading models); `see an example <https://github.com/IBM/ibm-generative-ai/blob/main/examples/user/langchain_serialization.py>`_.
* Added support for the Chat endpoint in ``Model`` class; see an `example <https://github.com/IBM/ibm-generative-ai/blob/main/examples/user/chat.py>`_.
* Added support for new moderation models (HAP, STIGMA, Implicit Hate) - not released on API yet but will be available soon.
* Added type validation for input_tokens property in generate response.
* Extend LangChain generation information / LLM Output (token_usage structure, generated tokens, stop_reason, conversation_id, created_at, ...).
* Add optional ``raw_response=True/False`` parameter to ``generate_stream`` / ``generate_as_complete`` and ``generate`` methods to receive a raw response instead of unwrapped results.

🐛 Bug fixes
^^^^^^^^^^^^^^^


* LangChain extension now correctly tokenizes the inputs (previously, the GPT2 tokenizer had been used).
* Improve general error handling.

**Full Changelog**: `v0.4.1...v0.5.0 <https://github.com/IBM/ibm-generative-ai/compare/v0.4.1...v0.5.0>`_


v0.4.1 (2023-10-27)
-------------------

🐛 Bug fixes
^^^^^^^^^^^^^^^


* Correctly handle file responses
* Use ``tqdm.auto`` instead of ``tqdm.tqdm`` to improve display in Jupyter Notebooks

**Full Changelog**: `v0.4.0...v0.4.1 <https://github.com/IBM/ibm-generative-ai/compare/v0.4.0...v0.4.1>`_


v0.4.0 (2023-10-24)
-------------------

⚠️ Switch to Pydantic V2
^^^^^^^^^^^^^^^^^^^^^^^^


* In case your application is dependent on Pydantic V1, refer to the `migration guide <https://docs.pydantic.dev/2.0/migration/>`_.
* If you cannot upgrade, stick to the previous version 0.3.2.

**Full Changelog**: `v0.3.2...v0.4.0 <https://github.com/IBM/ibm-generative-ai/compare/v0.3.2...v0.4.0>`_


v0.3.2 (2023-10-23)
-------------------

🐛 Bug fixes
^^^^^^^^^^^^^^^


* Correctly handle async errors and process abortion

🔧 Configuration Changes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


* Increase async generate/tokenize retry limits from 3 to 5

**Full Changelog**: `v0.3.1...v0.3.2 <https://github.com/IBM/ibm-generative-ai/compare/v0.3.1...v0.3.2>`_


v0.3.1 (2023-10-20)
-------------------

🚀 Features / Enhancements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


* Handle concurrency limits for ``generate`` and ``generate_as_completed`` methods.
* Add automatic handling of rate limits for the tokenize endpoint (tokenize_async method).
* Added ``stop_sequence`` parameter for generated output (non-empty token which caused the generation to stop) + added - ``include_stop_sequence`` parameter for the ``GenerateParams`` (it indicates whether the stop sequence (which caused the generation to stop) is part of the generated text. The default value depends on the model in use).
* Removed hidden ``stop_sequences`` removal inside the ``LangChainInterface``\ , which can now be controlled via the ``include_stop_sequence`` parameter.
* Improve general error handling + method signatures (improve Python typings).

🐛 Bug fixes
^^^^^^^^^^^^^^^


* Fix stacked progress bar (\ ``generate_async`` method)
* Handle cases when the package is used inside the ``asyncio`` environment
* Hide warning when an unknown field is retrieved in the generated response

**Full Changelog**: `v0.3.0...v0.3.1 <https://github.com/IBM/ibm-generative-ai/compare/v0.3.0...v0.3.1>`_


v0.3.0 (2023-10-12)
-------------------

🚀 Features / Enhancements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


* Added Hugging Face Agent support; see an `example <https://github.com/IBM/ibm-generative-ai/blob/main/examples/user/huggingface_agent.py>`_.
* Drastically improve the speed of ``generate_async`` method - the concurrency limit is now automatically inferred from the API. (custom setting of ``ConnectionManager.MAX_CONCURRENT_GENERATE`` will be ignored). In case you want to slow down the speed of generating, just pass the following parameter to the method: ``max_concurrency_limit=1``  or any other value.
* Increase the default tokenize processing limits from 5 requests per second to 10 requests per second (this will be increased in the future).

🐛 Bug fixes
^^^^^^^^^^^^^^^


* Throws on unhandled exceptions during the ``generate_async`` calls.
  Correctly cleanups the async HTTP clients when the task/calculation is being cancelled (for instance, you call generate_async in Jupyter - Notebook and then click the stop button). This should prevent receiving the ``Can't have two active async_generate_clients`` error.
* Fix async support for newer LangChain versions (\ ``>=0.0.300``\ )
* Fix LangChain PromptTemplate import warning in newer versions of LangChain
* Correctly handle server errors when streaming
* Fix ``tune_methods`` method


v0.2.8 (2023-09-25)
-------------------

🚀 Features / Enhancements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


* Added moderation support; now you can retrieve HAP for generated requests (\ `example <https://github.com/IBM/ibm-generative-ai/blob/main/examples/user/generate_with_moderation.py>`_\ )
* Internally improve streaming processing (poor or unstable internet connection)
* Internally improve server response parsing and error handling
* Add a user-agent header to distinguish Python SDK on the API

🐛 Bug fixes
^^^^^^^^^^^^^^^


* LangChain - correct handling of stop_sequences
* Correctly set versions of used dependencies (httpx / pyyaml)
* Prevents unexpected modifications to user's GenerateParams passed to the Model class
* Prevents unexpected errors when GenerateParams contains stream=True and generate (non-stream) version is called

🔧 Configuration changes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


* Remove API version from the API endpoint string

**Full Changelog**: `v0.2.7...v0.2.8 <https://github.com/IBM/ibm-generative-ai/compare/v0.2.7...v0.2.8>`_


v0.2.7 (2023-09-15)
-------------------


* feat(langchain) - generate method by @Tomas2D in `#157 <https://github.com/IBM/ibm-generative-ai/pull/157>`_
* fix(params): do not strip special characters by @Tomas2D in `#153 <https://github.com/IBM/ibm-generative-ai/pull/153>`_
* fix: correct httpx dependency version by @Tomas2D in `#158 <https://github.com/IBM/ibm-generative-ai/pull/158>`_

**Full Changelog**: `v0.2.6...v0.2.7 <https://github.com/IBM/ibm-generative-ai/compare/v0.2.6...v0.2.7>`_


v0.2.6 (2023-09-11)
-------------------


* feat(langchain): add streaming support by @Tomas2D in `#144 <https://github.com/IBM/ibm-generative-ai/pull/144>`_
* feat(http): allow override httpx options by @Tomas2D in `#149 <https://github.com/IBM/ibm-generative-ai/pull/149>`_
* feat: add typical_p parameter by @Tomas2D in `#135 <https://github.com/IBM/ibm-generative-ai/pull/135>`_
* chore: update examples by @Tomas2D in `#136 <https://github.com/IBM/ibm-generative-ai/pull/136>`_
* docs: mention CLI in README by @Tomas2D in `#143 <https://github.com/IBM/ibm-generative-ai/pull/143>`_
* chore: adding escapting of backslashes for re.sub value by @assaftibm in `#84 <https://github.com/IBM/ibm-generative-ai/pull/84>`_
* chore: correct README.md typo by @ind1go in `#148 <https://github.com/IBM/ibm-generative-ai/pull/148>`_
* update schema for stop_sequences generate param by @mirianfsilva in `#142 <https://github.com/IBM/ibm-generative-ai/pull/142>`_

New Contributors
^^^^^^^^^^^^^^^^


* @assaftibm made their first contribution in `#84 <https://github.com/IBM/ibm-generative-ai/pull/84>`_
* @ind1go made their first contribution in `#148 <https://github.com/IBM/ibm-generative-ai/pull/148>`_

**Full Changelog**: `v0.2.5...v0.2.6 <https://github.com/IBM/ibm-generative-ai/compare/v0.2.5...v0.2.6>`_


v0.2.5 (2023-08-21)
-------------------


* TOUs handling
* Update Pydantic version
* Update examples

**Full Changelog**: `v0.2.4...v0.2.5 <https://github.com/IBM/ibm-generative-ai/compare/v0.2.4...v0.2.5>`_


v0.2.4 (2023-08-01)
-------------------

Updated the documentation (imports of credentials)
Updated schemas for config
Added params in GeneratedParams
Updated examples
Updated tests


v0.2.3 (2023-07-24)
-------------------


* Remove ModelType enum
* Add utils for Model class: listing, info, available, etc.
* Pydantic model allows extra params
* Tests


v0.2.2 (2023-07-11)
-------------------

Documentation Updates.


v0.2.1 (2023-07-10)
-------------------

Documentation update
Example update


v0.2.0 (2023-07-10)
-------------------

Model Tuning
File manager
Tuning Manager
ModelType deprecation warning
Open Source documentation update


v0.1.19 (2023-06-30)
--------------------

Fixed pydantic version issue


v0.1.18 (2023-06-30)
--------------------

Watsonx Templating support
Documentation and examples' update
Parameters updated for upstream compatibility with sampling method
Retry mechanism update


v0.1.17 (2023-06-23)
--------------------


* Modifications to examples/tests to avoid sampling-related parameters with greedy decoding
* Updates to build process
* Modifications to error messages


v0.1.16 (2023-06-21)
--------------------


* Documentation update
* Local server example
* Open source contributions information
* Example endpoints updated


v0.1.15 (2023-06-08)
--------------------


* 🔨 GitHub Workflows
* ✨ Progress bar in async_generate function
* 🐛 Updating Terms of Use to use PATCH
* 🎨 Adding accessors attribute to model class
* ✨Search Space example and utils
* ✨ Localserver Extension
