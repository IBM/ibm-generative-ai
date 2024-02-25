from genai._utils.deprecated_schema_import import _log_deprecation_warning
from genai.schema._api import *
from genai.schema._api_removed_schemas import _removed_schemas
from genai.schema._endpoints import *
from genai.schema._extensions import *

_renamed_schemas = {
    "UserPromptResult": PromptResult,
    "PromptsResponseResult": PromptResult,
    "UserResponseResult": UserResult,
    "UserCreateResultApiKey": UserApiKey,
    "PromptRetrieveRequestParamsSource": PromptListSource,
}


def __getattr__(name):
    if name in globals():
        return globals()[name]

    if name in _removed_schemas:
        explanation, target = _removed_schemas[name]
        _log_deprecation_warning(key=f"{__name__}.{name}_removed", msg=explanation)
        return target

    if name in _renamed_schemas:
        target = _renamed_schemas[name]
        _log_deprecation_warning(
            key=f"{__name__}.{name}_renamed",
            msg=f"Class has been renamed from '{name}' to '{target.__name__}'.\n"
            f"This class alias will be removed in the following major release.",
        )
        return target

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
