import ast
import os
from pathlib import Path
from typing import Generator, Optional

from pydantic import BaseModel


class PythonFile(BaseModel):
    path: Path
    is_private: bool

    def get_relative_path(self, to: Path) -> str:
        return os.path.relpath(self.path.resolve(), to.resolve())

    def _find_code_start_line(self, content: str) -> int:
        DOCSTRING_DELIMITER = '"""'

        def count_docstring_occurrences(line: str) -> int:
            if line == DOCSTRING_DELIMITER:
                return 1

            return line.startswith(DOCSTRING_DELIMITER) + line.endswith(DOCSTRING_DELIMITER)

        lines = content.split("\n")
        counter = 0
        for idx, line in enumerate(lines):
            line = line.strip()
            counter += count_docstring_occurrences(line)

            if counter >= 2:
                counter = idx + 1
                break
        else:
            raise ValueError("No docstring has been found!")

        while counter < len(lines) and lines[counter].strip() == "":
            counter += 1

        return counter

    def meta(self) -> tuple[str, str, int]:
        source_code = self.path.read_text()

        tree = ast.parse(source_code)
        doc = ast.get_docstring(tree, clean=True)
        if doc is None or doc == "":
            raise ValueError(f"Missing docstring in '{self.path.resolve()}' file!")

        title, *description = doc.split("\n\n", maxsplit=1)
        code_start_line = self._find_code_start_line(source_code)

        return title.strip(), description[0].strip() if description else "", code_start_line


def get_rst_filename(path: str, *, prefix: str):
    rst_filename = f"{prefix}.{path.replace('/', '.').replace('.py', '')}"
    return rst_filename.replace(".__init__", "")


class PythonHierarchy(BaseModel):
    root: PythonFile
    examples: list[PythonFile]
    nested_roots: list[PythonFile]


def _to_file_instance(path: Path) -> PythonFile:
    filename = path.name
    is_private = filename.startswith("_")

    return PythonFile(
        path=path,
        is_private=is_private,
    )


def _find_python_files(
    directory: Path, *, pattern: str = "*.py", exclude: Optional[set[str]] = None
) -> list[PythonFile]:
    if not exclude:
        exclude = {}

    files = map(_to_file_instance, directory.glob(pattern))
    return [file for file in files if file.path.name not in exclude]


def find_python_examples(directory: Path, exclude: set[str]) -> Generator[PythonHierarchy, None, None]:
    for root in _find_python_files(directory, pattern="**/__init__.py"):
        root_dir = root.path.parent.resolve()

        examples = [
            e
            for e in _find_python_files(root_dir, pattern="*.py", exclude={"__init__.py"})
            if not e.is_private and e.get_relative_path(directory) not in exclude
        ]
        nested_roots = _find_python_files(root_dir, pattern="*/__init__.py")

        yield PythonHierarchy(
            root=root,
            examples=examples,
            nested_roots=nested_roots,
        )
