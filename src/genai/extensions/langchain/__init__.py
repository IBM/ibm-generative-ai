"""Extension for LangChain library"""

import warnings
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as get_package_version

from packaging.version import parse as parse_version

from genai.extensions.langchain.chat_llm import LangChainChatInterface
from genai.extensions.langchain.embeddings import LangChainEmbeddingsInterface
from genai.extensions.langchain.llm import LangChainInterface
from genai.extensions.langchain.template import (
    from_langchain_template,
    to_langchain_template,
)


def _verify_langchain_version():
    try:
        langchain_version = get_package_version("langchain")
        minimal_valid_version = parse_version("0.1.0")
        current_version = parse_version(langchain_version)

        if current_version < minimal_valid_version:
            warnings.warn(
                category=RuntimeWarning,
                stacklevel=4,
                message=f"You are using 'langchain' package version {current_version}. "
                f"Please do upgrade now to version >= {minimal_valid_version}.",
            )

    except PackageNotFoundError:
        pass


_verify_langchain_version()

__all__ = [
    "LangChainInterface",
    "LangChainChatInterface",
    "LangChainEmbeddingsInterface",
    "from_langchain_template",
    "to_langchain_template",
]
