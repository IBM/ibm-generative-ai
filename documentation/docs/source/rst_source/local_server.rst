Running Custom Models
=================================

|

An example of running a locally served model is provided `here <https://github.com/IBM/ibm-generative-ai/blob/main/examples/user/localserver/localserver.py/>`_. The steps below detail how this is done.

|

1. In a new Python file, import the ibm-generative-ai library and the local server extension.

.. code-block:: python

    from genai.extensions.localserver import CustomModel, LocalLLMServer
    from genai.model import Model
    from genai.schemas import GenerateParams, GenerateResult, TokenizeResult, TokenParams

|

2. Create your custom model.

The `CustomModel <https://github.com/IBM/ibm-generative-ai/blob/23f2a42a706b7fb8d99c21da0ddac909528ca1ba/examples/user/localserver/localserver.py#L26-57/>`_ is an Abstract Base Class that the user defines. It requires the following three things:

    * **model_id** - Allows the server to link the model to an incoming request by model ID.
    * **generate** - The function which generates some output.
    * **tokenize** - The function which generates tokenize output.

You can view the documentation for CustomModel `here <https://github.com/IBM/ibm-generative-ai/blob/23f2a42a706b7fb8d99c21da0ddac909528ca1ba/src/genai/extensions/localserver/custom_model_interface.py/>`_

3. Instantiate the Local Server with your model.

.. code-block:: python

    server = LocalLLMServer(models=[<your-model-class-name>])

|

4. Run the server.

**Start the server.**

.. code-block:: python

    with server.run_locally():

|

**Within this code block, get the credentials/connection details for the local server.**

.. code-block:: python

    creds = server.get_credentials()

|

**Instantiate parameters for text generation.**

Use the GenerateParams() method to instantiate the parameters. The schema for this method can be found `here <https://ibm.github.io/ibm-generative-ai/rst_source/genai.schemas.generate_params.html#genai.schemas.generate_params.GenerateParams/>`_.

|

**Instantiate a model proxy object to send your requests.**

.. code-block:: python

    model = Model(<your-model-class-name>.model_id, params=params, credentials=creds)

From there, you can call GenAI methods such as generate() and tokenize() as needed. Make sure to call the methods with the model proxy object.

For example: model.generate()
