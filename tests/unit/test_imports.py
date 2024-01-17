import importlib
import importlib.util
import inspect
import pkgutil
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path
from typing import Iterator

import pytest

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
def test_schemas_export_symbols_explicitly():
    """All `schema.py` modules export their symbols explicitly under __all__ module attribute."""
    import genai

    path = Path(genai.__file__)
    schemas_files: Iterator[Path] = path.parent.glob("**/schema.py")
    schema_modules = [SourceFileLoader(f.parent.name, str(f)).load_module() for f in schemas_files]
    assert schema_modules
    for module in schema_modules:
        assert module and module.__all__ and len(module.__all__) >= 1
