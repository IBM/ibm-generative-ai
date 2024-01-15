.. _getting-started:

Getting Started
===============

.. contents::
   :local:
   :class: this-will-duplicate-information-and-it-is-still-useful-here

.. _installation:

Installation
------------

.. code-block:: bash

    pip install --upgrade ibm-generative-ai

Prerequisites
^^^^^^^^^^^^^

- Python version >= 3.9

- pip version >= 22.0.1


Check your pip version with ``pip --version`` and if needed, run the following command to upgrade pip:

.. code-block:: bash

    pip install --upgrade "pip>=22.0.1"

.. _gen-ai-endpoint:

API / Credentials
-------------------

By default, SDK will use the following API endpoint: ``https://bam-api.res.ibm.com/``. However, if you wish to target a different API, you can do so by defining it with the ``api_endpoint`` argument when you instantiate the ``Credentials`` object.

Your ``.env`` file:

.. code-block:: ini

    GENAI_KEY=YOUR_GENAI_API_KEY
    GENAI_API=https://bam-api.res.ibm.com


Example initialization

.. code-block:: python

    import os
    from dotenv import load_dotenv
    from genai.credentials import Credentials

    load_dotenv()

    # if you are using standard ENV variable names (GENAI_KEY / GENAI_API)
    credentials = Credentials.from_env()

    # or if you are using different ENV variable names
    credentials = Credentials.from_env(api_key_name="MY_ENV_KEY_NAME", api_endpoint_name="MY_ENV_ENDPOINT_NAME")

    # or if you want to pass values directly
    credentials = Credentials(api_key="MY_API_KEY", api_endpoint="MY_ENDPOINT")


How to work with SDK?
---------------------

The latest version of SDK reflects the latest version of the API (versions are handled automatically).
The main ``Client`` class serves as an entry point to the API, while its attributes refer to logically nested services.
This approach reflects the Rest API Structure; all request parameters remains the same (SDK does not alter them).

.. code-block:: python

    from genai import Client, Credentials

    credentials = Credentials(api_key="...") # or load from ENV via Credentials.from_env()
    client = Client(credentials=credentials)

    # client.text (sub-client for all text related tasks)

    # client.text.generation
    client.text.generation.create(...)
    client.text.generation.create_stream(...)

    # client.text.chat
    client.text.chat.create(...)
    client.text.chat.create_stream(...)

    # client.text.embedding
    client.text.embedding.create(...)

    # client.tokenization
    client.text.tokenization.create(...)

    # client.moderation
    client.text.moderation.create(...)

    # client.model
    client.model.list(...)
    client.model.retrieve(...)

    # client.tune
    client.tune.create(...)
    client.tune.list(...)
    client.tune.types(...)
    client.tune.retrieve(...)
    client.tune.delete(...)

    # client.prompt
    client.prompt.create(...)
    client.prompt.list(...)
    client.prompt.retrieve(...)
    client.prompt.delete(...)
    client.prompt.update(...)

    # client.user
    client.user.create(...)
    client.user.retrieve(...)

    # client.request
    client.request.list(...)
    client.request.chat(...)
    client.request.delete(...)
    client.request.chat_delete(...)

    # client.file
    client.file.list(...)
    client.file.retrieve(...)
    client.file.delete(...)
    client.file.read(...)



🚀 To see concrete examples, visit the :doc:`examples page <rst_source/examples>`.

Networking
^^^^^^^^^^

By default, requests time out after 10 minutes (connection timeout is 10 seconds).
Connection errors and some HTTP status codes are automatically retried.
This behaviour can be changed by altering the ``ApiClient`` settings (see examples).


Versioning
^^^^^^^^^^

Each SDK release is only compatible with the latest API version at the time of release. To use the SDK with an older API version, you need to download a version of the SDK tied to the API version you want. Look at the Changelog to see which SDK version to download.


Types / Schemas
^^^^^^^^^^^^^^^

Wast the majority of service methods accepts complex parameters either as instances of appropriate Pydantic class or plain dictionary which is converted to the Pydantic class under the hood.
Analogy with enums - you can pass either enum's value or a plain string. Types for inputs/outputs are automatically generated from the OpenAPI definition to Pydantic models.
Responses are thus automatically validated and provides various built-in helper functions to the user.


Logging
^^^^^^^

SDK uses the standard python `logging module <https://docs.python.org/3/library/logging.html>`_ for logging messages within the module.
Unless the consuming application explicitly enables logging, no logging messages from GenAI should appear in stdout or stderr e.g. no `print` statements, we should also always log to the `genai` namespace so that logs are easily identifiable.

Error Handling
^^^^^^^^^^^^^^

SDK exception classes (besides Python's built-in) can be imported from ``genai.exceptions``.

Validation errors

- ``ValueError``, ``TypeError``
- ``ValidationError`` - Pydantic class

API / Network errors

- ``ApiNetworkException`` - Unhandled network error (timeout, `httpx` error).
- ``ApiResponseException`` - Real API response with non 2xx status code.


Example can be found :ref:`here <examples.extra.error_handling>`.


Citation
--------

If this SDK has been significant in your research, and you would like to acknowledge
the project in your academic publication, please use the following citation scheme.

BibLaTeX
^^^^^^^^

.. code-block:: bibtex

    @online{ibm_generative_ai_sdk,
      author       = {IBM},
      title        = {IBM Generative AI Python SDK (Tech Preview)},
      url          = {https://github.com/IBM/ibm-generative-ai},
      year         = {YYYY},
      urldate      = {YYYY-MM-DD}
    }


BibTex
^^^^^^

.. code-block:: bibtex

    @misc{ibm_generative_ai_sdk,
      author       = {IBM},
      title        = {IBM Generative AI Python SDK (Tech Preview)},
      howpublished = {\url{https://github.com/IBM/ibm-generative-ai}},
      note         = {Accessed: YYYY-MM-DD},
      year         = {YYYY}
    }
