# Getting Started Guideline

## <a name='TableofContents'></a>Table of Contents

- [Table of Contents](#table-of-contents)
- [Installation](#installation)
- [Gen AI Endpoint](#gen-ai-endpoint)
  - [Example](#example)
- [Examples](#examples)
  - [Async Example](#async-example)
  - [Synchronous Example](#synchronous-example)
- [Tips and Troubleshooting](#tips-and-troubleshooting)
  - [Model Availability](#model-availability)
  - [Enabling Logs](#enabling-logs)
  - [Experimenting with a Large Number of Prompts](#many-prompts)
- [Extensions](#extensions)
  - [LangChain Extension](#langchain-extension)
- [Support](#support)

## <a name='Installation'></a>Installation

```bash
pip install ibm-generative-ai
```

#### <a name='KnownIssueFixes:'></a>Known Issue Fixes:

- **[SSL Issue]** If you run into "SSL_CERTIFICATE_VERIFY_FAILED" please run the following code snippet here: [support](SUPPORT.md).

### <a name='Prerequisites'></a>Prerequisites

Python version >= 3.9

Pip version >= 22.0.1

Check your pip version with `pip --version` and if needed run the following command to upgrade pip.

```bash
pip install --upgrade "pip>=22.0.1"
```

## <a name='GenAIEndpoint'></a>Gen AI Endpoint

By default, IBM Generative AI will use the following API endpoint: `https://workbench-api.res.ibm.com/v1/`. However, if you wish to target a different Gen AI API, you can do so by defining it with the `api_endpoint` argument when you instansiate the `Credentials` object.

### <a name='Example'></a>Example

Your `.env` file:

```ini
GENAI_KEY=YOUR_GENAI_API_KEY
GENAI_API=https://workbench-api.res.ibm.com/v1/
```

```python
import os

from dotenv import load_dotenv

from genai.credentials import Credentials

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint>
load_dotenv()
my_api_key = os.getenv("GENAI_KEY", None)
my_api_endpoint = os.getenv("GENAI_API", None)

# creds object
creds = Credentials(api_key=my_api_key, api_endpoint=my_api_endpoint)

# Now start using GenAI!

```

## <a name='Examples'></a>Examples

There are a number of examples you can try in the [`examples/user`](examples/user) directory.
Login to [workbench.res.ibm.com](https://workbench.res.ibm.com/) and get your GenAI API key. Then, create a `.env` file and assign the `GENAI_KEY` value as below example. [More information](#gen-ai-endpoint)

```ini
GENAI_KEY=YOUR_GENAI_API_KEY
# GENAI_API=GENAI_API_ENDPOINT << for a different endpoint
```

### <a name='AsyncExample'></a>Async Example

```python
import os

from dotenv import load_dotenv

from genai.credentials import Credentials
from genai.model import Model
from genai.schemas import GenerateParams

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_endpoint = os.getenv("GENAI_API", None)

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
creds = Credentials(api_key, api_endpoint)
# model object
model = Model("google/flan-ul2", params=params, credentials=creds)

greeting = "Hello! How are you?"
lots_of_greetings = [greeting] * 1000
num_of_greetings = len(lots_of_greetings)
num_said_greetings = 0
greeting1 = "Hello! How are you?"

# yields batch of results that are produced asynchronously and in parallel
for result in model.generate_async(lots_of_greetings):
    if result is not None:
        num_said_greetings += 1
        print(f"[Progress {str(float(num_said_greetings/num_of_greetings)*100)}%]")
        print(f"\t {result.input_text} --> {result.generated_text}")

```

If you are planning on sending a large number of prompts _and_ using logging, you might want to re-direct genai logs to a file instead of stdout.
Check the section [Tips and TroubleShooting](#tips-and-troubleshooting) for further help.

### <a name='SynchronousExample'></a>Synchronous Example

```python
import os

from dotenv import load_dotenv

from genai.credentials import Credentials
from genai.model import Model
from genai.schemas import GenerateParams

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<genai-api-endpoint>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_endpoint = os.getenv("GENAI_API", None)

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
creds = Credentials(api_key, api_endpoint)
# model object
model = Model("google/flan-ul2", params=params, credentials=creds)

greeting1 = "Hello! How are you?"
greeting2 = "I am fine and you?"

# Call generate function
responses = model.generate_as_completed([greeting1, greeting2] * 4)
for response in responses:
    print(f"Generated text: {response.generated_text}")

```

## <a name='TipsAndTroubleshooting'></a>Tips and Troubleshooting

### <a name='Model Availability'></a>Model Availability

To test the reachability of your endpoint and availability of desired model, use the following utility script with your model details:

```python
import os

from dotenv import load_dotenv

from genai.credentials import Credentials
from genai.model import Model

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
# GENAI_API=<your-genai-api endpoint>
load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_url = os.getenv("GENAI_API", None)
creds = Credentials(api_key, api_endpoint=api_url)

print("======= List of all available models =======")
for m in Model.models(credentials=creds):
    print(m)

print("====== Checking availability of a specific model =======")
model_id = "<string-id-of-model>"
model = Model(model_id, params=None, credentials=creds)
print(f"Model availability for {model_id}: {model.available()}")

print("====== Display model card =======")
model = Model(model_id, params=None, credentials=creds)
model_info = model.info()
print(f"Model info for {model_id}: \n{model_info}")
print(f"Extract fields from model card (e.g., token_limit): {model_info.token_limit}")
```

### <a name='EnablingLogs'></a>Enabling Logs

If you're building an application or example and would like to see the GENAI logs, you can enable them in the following way:

```python
import logging
import os

# Most GENAI logs are at Debug level.
logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))
```

If you only want genai logs, or those logs at a specific level, you can set this using the following syntax:

```python
logging.getLogger("genai").setLevel(logging.DEBUG)
```

Example log message from GENAI:

```log
DEBUG:genai.model:Model Created:  Model: google/flan-t5-xxl, endpoint: https://workbench-api.res.ibm.com/v1/
```

Example of directing genai logs to a file:

```python
# create file handler which logs even debug messages
fh = logging.FileHandler('genai.log')
fh.setLevel(logging.DEBUG)
logging.getLogger("genai").addHandler(fh)
```

To learn more about logging in python, you can follow the tutorial [here](https://docs.python.org/3/howto/logging.html).

### <a name='ManyPrompts'></a>Experimenting with a Large Number of Prompts

Since generating responses for a large number of prompts can be time-consuming and there could be unforeseen circumstances such as internet connectivity issues, here are some strategies
to work with:

- Start with a small number of prompts to prototype the code. You can enable logging as described above for debugging during prototyping.
- Include exception handling in sensitive sections such as callbacks.
- Checkpoint/save prompts and received responses periodically.
- Check examples in `examples/user` directory and modify them for your needs.

```python
def my_callback(result):
    try:
        ...
    except:
        ...

outputs = []
count = 0
for result in model.generate_async(prompts, callback=my_callback):
    if result is not None:
        print(result.input_text, " --> ", result.generated_text)
        # check if prompts[count] and result.input_text are the same
        outputs.append((result.input_text, result.generated_text))
        # periodically save outputs to disk or some location
        ...
    else:
        # ... save failed prompts for retrying
    count += 1
```

## <a name='Extensions'></a>Extensions

GenAI currently supports a langchain extension and more extensions are in the pipeline. Please reach out to
us if you want support for some framework as an extension or want to design an extension yourself.

### <a name='LangChainExtension'></a>LangChain Extension

Install the langchain extension as follows:

```bash
pip install "ibm-generative-ai[langchain]"
```

Currently the langchain extension allows IBM Generative AI models to be wrapped as Langchain LLMs and translation between genai PromptPatterns and LangChain PromptTemplates. Below are sample snippets

```python
import os
from dotenv import load_dotenv
import genai.extensions.langchain
from genai.extensions.langchain import LangChainInterface
from genai.schemas import GenerateParams
from genai import Credentials, Model, PromptPattern

load_dotenv()
api_key = os.getenv("GENAI_KEY", None)
api_endpoint = os.getenv("GENAI_API", None)
creds = Credentials(api_key, api_endpoint)
params = GenerateParams(decoding_method="greedy")

# As LangChain Model
langchain_model = LangChainInterface(model="google/flan-ul2", params=params, credentials=creds)
print(langchain_model("Answer this question: What is life?"))

# As GenAI Model
genai_model = Model(model="google/flan-ul2", params=params, credentials=creds)
print(genai_model.generate(["Answer this question: What is life?"])[0].generated_text)

# GenAI prompt pattern to langchain PromptTemplate and vice versa
seed_pattern = PromptPattern.from_str("Answer this question: {{question}}")
template = seed_pattern.langchain.as_template()
pattern = PromptPattern.langchain.from_template(template)

print(langchain_model(template.format(question="What is life?")))
print(genai_model.generate([pattern.sub("question", "What is life?")])[0].generated_text)
```

## <a name='Support'></a>Support

Need help? Check out how to get [support](SUPPORT.md)
