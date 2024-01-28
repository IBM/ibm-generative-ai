import importlib
import importlib.util
import inspect
import pkgutil
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path
from typing import Iterator

import pytest

import genai.schema
from genai._utils.service import BaseService


def _import_submodules(package_name):
    """Import all submodules of a module, recursively (taken from https://stackoverflow.com/a/25083161)

    :param package_name: Package name
    :type package_name: str
    :rtype: dict[types.ModuleType]
    """
    package = sys.modules[package_name]
    return {
        name: importlib.import_module(package_name + "." + name)
        for loader, name, is_pkg in pkgutil.walk_packages(package.__path__)
    }


def _get_all_subclasses(cls: type) -> list[type]:
    subclasses = cls.__subclasses__()
    for subclass in subclasses:
        subclasses.extend(_get_all_subclasses(subclass))
    return subclasses


@pytest.mark.unit
def test_services_export_symbols_explicitly():
    """All services export their symbols explicitly under __all__ module attribute."""

    _import_submodules("genai")  # import everything to register all subclasses
    classes_to_check = _get_all_subclasses(BaseService)
    # ignore subclasses classes defined in tests
    classes_to_check = [clazz for clazz in classes_to_check if clazz.__module__.startswith("genai")]

    for clazz in classes_to_check:
        module = inspect.getmodule(clazz)
        assert module and module.__all__
        assert clazz.__name__ in module.__all__


@pytest.mark.unit
def test_backwards_compatibility(propagate_caplog):
    """

    Note: The following schemas were removed without any deprecation warning as they were not part of any public API:
      - FileRetrieveParametersQuery
      - ModelRetrieveParametersQuery
      - RequestRetrieveParametersQuery
      - TuneRetrieveParametersQuery
      - TextGenerationComparisonCreateRequest
    """
    previously_exported_symbols = [
        "AIMessage",
        "BaseMessage",
        "ChatRole",
        "DecodingMethod",
        "FileCreateResponse",
        "FileIdRetrieveResponse",
        "FileListSortBy",
        "FilePurpose",
        "FileRetrieveResponse",
        "HAPOptions",
        "HumanMessage",
        "ImplicitHateOptions",
        "LengthPenalty",
        "ModelIdRetrieveResponse",
        "ModelIdRetrieveResult",
        "ModelRetrieveResponse",
        "ModelTokenLimits",
        "ModerationHAP",
        "ModerationImplicitHate",
        "ModerationParameters",
        "ModerationPosition",
        "ModerationStigma",
        "ModerationTokens",
        "PromptCreateResponse",
        "PromptIdRetrieveResponse",
        "PromptIdUpdateResponse",
        "PromptRetrieveRequestParamsSource",
        "PromptRetrieveResponse",
        "PromptTemplate",
        "PromptTemplateData",
        "PromptType",
        "RequestApiVersion",
        "RequestChatConversationIdRetrieveResponse",
        "RequestEndpoint",
        "RequestOrigin",
        "RequestRetrieveResponse",
        "RequestStatus",
        "SortDirection",
        "StigmaOptions",
        "StopReason",
        "SystemMessage",
        "TextChatCreateResponse",
        "TextChatStreamCreateResponse",
        "TextEmbeddingCreateResponse",
        "TextEmbeddingLimit",
        "TextEmbeddingParameters",
        "TextGenerationComparisonCreateRequestRequest",
        "TextGenerationComparisonCreateResponse",
        "TextGenerationComparisonParameters",
        "TextGenerationCreateResponse",
        "TextGenerationFeedbackCategory",
        "TextGenerationIdFeedbackCreateResponse",
        "TextGenerationIdFeedbackRetrieveResponse",
        "TextGenerationIdFeedbackUpdateResponse",
        "TextGenerationLimitRetrieveResponse",
        "TextGenerationParameters",
        "TextGenerationResult",
        "TextGenerationReturnOptions",
        "TextGenerationStreamCreateResponse",
        "TextModeration",
        "TextModerationCreateResponse",
        "TextTokenizationCreateResponse",
        "TextTokenizationCreateResults",
        "TextTokenizationParameters",
        "TextTokenizationReturnOptions",
        "TrimMethod",
        "TuneAssetType",
        "TuneCreateResponse",
        "TuneIdRetrieveResponse",
        "TuneParameters",
        "TuneResult",
        "TuneRetrieveResponse",
        "TuneStatus",
        "TuningType",
        "TuningTypeRetrieveResponse",
        "UserCreateResponse",
        "UserPatchResponse",
        "UserRetrieveResponse",
    ]
    # name is available in schema
    for name in previously_exported_symbols:
        getattr(genai.schema, name)


@pytest.mark.unit
def test_backwards_compatibility_warnings(propagate_caplog):
    caplog = propagate_caplog("genai.schema")
    # Try a few imports from services:

    services = [
        "file",
        "model",
        "prompt",
        "request",
        "text.chat",
        "text.embedding",
        "text.embedding.limits",
        "text.generation",
        "text.generation.feedback",
        "text.generation.limit",
        "text.moderation",
        "text.tokenization",
        "tune",
        "user",
    ]
    services = ["file"]
    example_symbol = "DecodingMethod"
    for service in services:
        module = f"genai.{service}"
        with caplog.at_level("WARNING"):
            exec(f"from {module} import {example_symbol}")
            assert f"Deprecated import of {example_symbol} from module {module}" in caplog.text


@pytest.mark.unit
def test_schemas_export_symbols_explicitly():
    """All `schema.py` modules export their symbols explicitly under __all__ module attribute."""
    import genai

    path = Path(genai.__file__)
    schemas_files: Iterator[Path] = path.parent.glob("**/schema.py")
    schema_modules = [SourceFileLoader(f.parent.name, str(f)).load_module() for f in schemas_files]
    assert schema_modules
    for module in schema_modules:
        assert module and module.__all__ and len(module.__all__) >= 1
