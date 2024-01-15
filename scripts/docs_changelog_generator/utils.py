import unicodedata
from pathlib import Path

from gitchangelog.gitchangelog import GitCommit, GitRepos

DEFAULT_REPO_URL = "https://github.com/IBM/ibm-generative-ai"


def output_engine_pipeline(render_fn):
    def _process(output_engine):
        return lambda data, opts: output_engine(*render_fn(data, opts))

    return _process


class GithubRSTLinks:
    def __init__(self, repo_url=DEFAULT_REPO_URL):
        self._repo_url = repo_url

    def _link(self, text: str, url: str):
        return f"`{text} <{url}>`_"

    def link_to_user(self, username: str) -> str:
        return self._link(f"@{username}", f"https://github.com/{username}")

    def link_to_pr(self, pr_id: str) -> str:
        return self._link(f"#({pr_id})", f"{self._repo_url}/pull/{pr_id}")

    def link_to_compare(self, ref1: str, ref2: str) -> str:
        return f'**Full Changelog**: {self._link(f"{ref1}...{ref2}", f"{self._repo_url}/compare/{ref1}...{ref2}")}'


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
