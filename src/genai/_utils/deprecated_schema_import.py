import logging

_CACHED_WARNINGS: set[str] = set()
logger = logging.getLogger(__name__)


def _log_deprecation_warning(name: str, module_name: str):
    cache_warning_name = f"{module_name}.{name}"

    if cache_warning_name in _CACHED_WARNINGS:
        return

    _CACHED_WARNINGS.add(cache_warning_name)
    logger.warning(
        f"Deprecated import of {name} from module {module_name}. Please use `from genai.schema import {name}`."
    )


def _deprecated_schema_import(name: str, module_name: str):
    import genai.schema

    if name in dir(genai.schema) and not name.startswith("_"):
        _log_deprecation_warning(name, module_name)
        return getattr(genai.schema, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
