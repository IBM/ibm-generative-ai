from operator import itemgetter
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel

from docs_examples_generator.config import DefaultGeneratorConfig, GeneratorConfig
from docs_examples_generator.logger import get_logger
from docs_examples_generator.utils import (
    PythonFile,
    PythonHierarchy,
    find_python_examples,
    get_rst_filename,
)

load_dotenv()

dirname = Path(__file__).parent.absolute()
logger = get_logger(__name__)


class PythonExample(BaseModel):
    title: str
    description: str
    path: Path


def _create_python_example(py_file: PythonFile, *, relative_path: str, config: GeneratorConfig) -> PythonExample:
    rst_filename = get_rst_filename(relative_path, prefix=config.module_name)
    path = Path(config.output_directory, f"{rst_filename}.rst")

    title, description, code_start_line = py_file.meta()
    path.write_text(
        data="\n".join(
            [
                f".. _{rst_filename}:",
                "",
                *[title, "=" * len(title)],
                "",
                description,
                "",
                f".. literalinclude:: {py_file.get_relative_path(config.output_directory)}",
                "\t:language: python",
                f"\t:caption: See `{py_file.path.name} <{config.input_directory_href}/{relative_path}>`_ on GitHub.",
                f"\t:lines: {code_start_line + 1}-",
                "",
            ]
        )
    )
    return PythonExample(path=path, title=title, description=description)


def _create_python_examples_toc(hierarchy: PythonHierarchy, config: GeneratorConfig):
    def _get_rst_filename(file: PythonFile):
        relative_path = file.get_relative_path(config.input_directory)
        return get_rst_filename(relative_path, prefix=config.module_name)

    def _get_sorted_nested_roots() -> list[PythonFile]:
        module_order = config.modules_order.get(_get_rst_filename(hierarchy.root), [])
        if not module_order:
            return hierarchy.nested_roots

        # Achieve partially sorting by using min-heap
        roots_with_order: list[tuple[int, PythonFile]] = []
        for idx, root in enumerate(hierarchy.nested_roots, start=len(hierarchy.nested_roots)):
            rst_name = _get_rst_filename(root)
            order = module_order.index(rst_name) + 1 if rst_name in module_order else idx
            roots_with_order.append((order, root))

        roots_with_order.sort(key=itemgetter(0))
        return list(map(itemgetter(1), roots_with_order))

    rst_filename = _get_rst_filename(hierarchy.root)
    path = Path(config.output_directory, f"{rst_filename}.rst")
    [title, description, *_] = hierarchy.root.meta()
    path.write_text(
        data="\n".join(
            [
                f".. _{rst_filename}:",
                "",
                *[title, "=" * len(title)],
                "",
                description,
                "",
                ".. toctree::",
                "",
                *[f"\t{_get_rst_filename(example)}" for example in hierarchy.examples],
                *[f"\t{_get_rst_filename(root)}" for root in _get_sorted_nested_roots()],
                "",
            ]
        )
    )

    return path


def run(config: GeneratorConfig):
    logger.info(f"Loading Python Examples from '{config.input_directory.resolve()}'")

    for hierarchy in find_python_examples(config.input_directory, exclude=config.exclude):
        _create_python_examples_toc(hierarchy, config)

        for py_file in hierarchy.examples:
            relative_path = py_file.get_relative_path(config.input_directory)

            logger.info(f"Processing {py_file.path.resolve()}!")
            py_example = _create_python_example(py_file, relative_path=relative_path, config=config)
            logger.info(f"-> output has been saved to {py_example.path.resolve()}!")

    logger.info("")
    logger.info("Done!")


if __name__ == "__main__":
    try:
        run(config=DefaultGeneratorConfig)
    except Exception as e:
        logger.error(e, exc_info=True)
        exit(1)
