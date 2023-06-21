# IBM Generative AI Extensions Guide
Open-source contributors are welcome to extend IBM Gen AI functionality via extensions that must keep the IBM Gen AI package as a dependency. This document explains what extensions are, the types of extensions that exist, and how to create them.

# Table of Contents
- [About the core package](#ibm-generative-ai-core-package)
- [What is an extension?](#what-is-an-ibm-generative-ai-extension)
- [Types of extensions](#ibm-generative-ai-extension-types)
- [Extensions migration](#extensions-migration)
- [Design considerations](#design-considerations-to-build-extensions)

# IBM Generative AI Core Package
[IBM Generative AI open-source repository](https://github.com/IBM/ibm-generative-ai) lives under [IBM Github organization](https://github.com/IBM/). This repository is the official and unique location of IBM Gen AI core package source code.

# What is an IBM Generative AI Extension?
An extension is a software add-on that is installed on a program to enhance its capabilities. Gen AI extensions are meant to expand the capabilities of the Gen AI core package. For instance, imagine that you want to build a prompt pattern with data from a pandas dataframe. You could write your own code  to achive such functionaliy, or you could instead use the Gen AI Pandas extension. Using the extension will allow you to save development time and deliver an elegant solution that re-uses code when it is possible.

# IBM Generative AI Extension types
IBM Generative AI extensions can be either of the following :
- official open-source extensions (supported by the project team)
- third-party open-source extensions

## Open-source "Gen AI official" extensions
Extensions that are meant for public use from the get-go should instead be developed as official open-source extensions. Examples of official extensions that have already been released are LangChain, Pandas, and Hugging Face extensions.

### Ownership and location
Open-source extensions should be submitted directly to the [IBM Generative AI open-source repository](https://github.com/IBM/ibm-generative-ai) and should be developed following the [open-source Gen AI contribution guide](https://github.com/IBM/ibm-generative-ai/blob/main/DEVELOPMENT.md). Open-source official extensions are typically developed by the Gen AI team, or in collaboration with them. Providing maintenance to open-source official extensions is responsability of the Gen AI team.

## Open-source "third-party" extensions
All other extensions neither implemented nor officially maintained by the Gen AI team are referred to as open-source third-party extensions.

### Ownership and location
Open-source third-party extensions can live anywhere, inside [IBM organization](https://github.com/IBM/), the wider Github universe, or other contributors' own Github spaces (e.g., other IBM teams, clients, partners). Maintaining these extensions would be the responsibility of their owners.

# Extensions migration
Extensions might be migrated from one type to another upon evaluation and approval of the Gen AI maintenance team. Below, we describe two common migration scenarios:

## Open-source "third-party" to open-source "Gen AI official"
If open-source third-party contributors have an interest in their extensions becoming official, they must contact the IBM Gen AI team. The Gen AI team will evaluate the request considering novelty and implementation quality (meaning it was developed following the Gen AI official guide and meets Gen AI extensions' design considerations). If the request is approved, the Gen AI team will assist the extension owners in migrating the extension.

## Open-source "Gen AI official" to Gen AI's core
Upon evaluation of the Gen AI maintenance team, open-source extensions could be merged with Gen AI core code and become deprecated as extensions. Deprecation announcements will be shared as part of the release notes of every new version of the IBM Gen AI package.

# Design considerations to build extensions
Among other patterns, a developer should consider a mix-and-match of the two following important development experience patterns to design an extension for IBM Gen AI SDK:

## Extensions that simulate being part of a core class

In spite of the extension's code living in a separate location, **try to give the impression that extended functionality is part of an IBM Gen AI core class**.

The code snippet below shows an example of this pattern. While `from_template` method is part of an extension class (`PromptExtension`) and not a core class (`PromptPattern`), the way it is being called gives end-users the impression that the method is part of the `PromptPattern` core class. The magic that enables providing this development experience is the use of decorators at import time. This pattern enables extending user-facing classes in a user-friendly way.

```python
genai_prompt_pattern = PromptPattern.langchain.from_template(langchain_prompt_template)
# notice langchain hook in the function call.
```

## Extensions that wrap core class functionality

Designing extensions that do not integrate, but **wrap functionality in Gen AI's core** for common use cases. These classes are meant to be used as entities on their own.

The `LangChainInterface` class (see below) is an example of this pattern. `LangChainInterface` is a subclass of langchain's `LLM` class that wraps `generate` functionality of Gen AI's Model.

```python
...

try:
    from langchain.llms.base import LLM
    from langchain.llms.utils import enforce_stop_tokens
except ImportError:
    raise ImportError("Could not import langchain: Please install ibm-generative-ai[langchain] extension.")

...

class LangChainInterface(LLM, BaseModel):
```

Click [here](https://github.com/IBM/ibm-generative-ai/blob/main/src/genai/extensions/langchain/llm.py)" to check the full definition of this class.
