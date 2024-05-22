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
