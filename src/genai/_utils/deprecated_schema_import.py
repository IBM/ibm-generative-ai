import warnings

_CACHED_WARNINGS: set[str] = set()


def _print_deprecation_warning(msg: str):
    with warnings.catch_warnings():
        warnings.simplefilter("always", DeprecationWarning)
        warnings.warn(msg, category=DeprecationWarning, stacklevel=4)  # the original import is 4 levels higher


def _log_deprecation_warning(key: str, msg: str):
    if key in _CACHED_WARNINGS:
        return

    _print_deprecation_warning(msg)

    _CACHED_WARNINGS.add(key)


def _deprecated_schema_import(name: str, module_name: str):
    """
    Support for deprecated import style "from genai.text.generation import" -> should be "from genai.schema import"

    TODO(#297): to be removed in next major version
    """
    import genai.schema

    if name in dir(genai.schema) and not name.startswith("_"):
        key = f"{module_name}.{name}"
        _log_deprecation_warning(
            key,
            f"Deprecated import of {name} from module {module_name}. Please use `from genai.schema import {name}`.",
        )
        return getattr(genai.schema, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
