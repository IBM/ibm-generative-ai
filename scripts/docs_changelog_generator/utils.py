import contextlib
import unicodedata
from contextvars import ContextVar
from pathlib import Path
from typing import TypeVar

from gitchangelog.gitchangelog import GitCommit, GitRepos

from docs_changelog_generator.config import config_context_var


def output_engine_pipeline(render_fn):
    config = config_context_var.get()

    def _process(output_engine):
        return lambda data, opts: output_engine(*render_fn(data, opts, config))

    return _process


class GithubRSTLinks:
    def __init__(self, repo_url: str):
        self._repo_url = repo_url

    def _link(self, text: str, url: str):
        return f"`{text} <{url}>`_"

    def link_to_user(self, username: str) -> str:
        return self._link(f"@{username}", f"https://github.com/{username}")

    def link_to_pr(self, pr_id: str) -> str:
        return self._link(f"#({pr_id})", f"{self._repo_url}/pull/{pr_id}")

    def link_to_compare(self, ref1: str, ref2: str) -> str:
        return self._link(f"{ref1}...{ref2}", f"{self._repo_url}/compare/{ref1}...{ref2}")


def shave_marks(txt: str) -> str:
    """Remove diacritics, taken from the Fluent Python book"""
    # 1) decompose into base characters and combinding marks i.e. 'cafe\N{COMBINING ACUTE ACCENT}'
    norm_txt = unicodedata.normalize("NFD", txt)
    # 2) shave - remove all combining marks
    shaved = "".join(c for c in norm_txt if not unicodedata.combining(c))
    # 3) recompose all characters
    return unicodedata.normalize("NFC", shaved)


def get_git_tags() -> list[GitCommit]:
    repository = GitRepos(Path(__file__).parent.absolute())
    return repository.tags()


T = TypeVar("T")


@contextlib.contextmanager
def use_context(context_var: ContextVar[T], value: T) -> None:
    reset_token = context_var.set(value)
    try:
        yield
    finally:
        context_var.reset(reset_token)
