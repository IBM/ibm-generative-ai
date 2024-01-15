import os
import re
import textwrap
from pathlib import Path

import yaml
from _common.logger import get_logger
from dotenv import load_dotenv
from tabulate import tabulate

from docs_changelog_generator.utils import GithubRSTLinks, get_git_tags, output_engine_pipeline, shave_marks
from genai._generated.endpoints import ApiEndpoint

load_dotenv()

logger = get_logger(__name__)
DIRNAME = Path(__file__).parent.absolute()
GITCHANGELOG_CONFIG_FILENAME = str(DIRNAME / Path("config.py"))
AUTHOR_NAMES_MAPPING_PATH = Path(__file__).parent.absolute() / Path("authors_by_name.yaml")

github_links = GithubRSTLinks()


@output_engine_pipeline
def inject_versions(data, opts):
    rows = [[endpoint.method, endpoint.path, endpoint.version] for endpoint in ApiEndpoint.__subclasses__()]
    versions_table = tabulate(rows, headers=["Method", "Path", "Version (YYYY-MM-DD)"], tablefmt="rst")

    data["api_versions_table"] = "\n".join(
        [
            "🔗 API Endpoint Versions",
            "^^^^^^^^^^^^^^^^^^^^^^^^",
            "",
            ".. collapse:: API Endpoint Versions",
            "",
            textwrap.indent(versions_table, " " * 4),
        ]
    )
    return data, opts


@output_engine_pipeline
def inject_author_usernames(data, opts):
    with open(AUTHOR_NAMES_MAPPING_PATH) as f:
        author_names_map = yaml.safe_load(f)
    if not isinstance(data["versions"], list):
        data["versions"] = list(data["versions"])
    for version in data["versions"]:
        commits = [commit for section in version["sections"] for commit in section["commits"]]
        for commit in commits:
            resolved_author_names = []
            for author in commit["authors"]:
                author_shaved = shave_marks(author)
                if author_shaved not in author_names_map:
                    logger.warn(f'Author "{author}" not found in {AUTHOR_NAMES_MAPPING_PATH}')
                    resolved_author_names.append(author)
                else:
                    resolved_author_names.append(github_links.link_to_user(author_names_map[author_shaved]))
            commit["author_names_resolved"] = ", ".join(resolved_author_names)
    return data, opts


@output_engine_pipeline
def inject_compare_link(data, opts):
    if not isinstance(data["versions"], list):
        data["versions"] = list(data["versions"])

    tags = get_git_tags()

    for version in data["versions"]:
        if version["tag"] is None:
            link = github_links.link_to_compare(tags[-1].identifier, "HEAD")  # latest ... HEAD
        else:
            version_index = tags.index(version["tag"])
            link = github_links.link_to_compare(tags[version_index].identifier, tags[version_index - 1].identifier)
        version["full_changelog_link"] = link
    return data, opts


def subject_process(text):
    pr_pattern = re.compile(r"\(#([0-9]+)\)$")
    [pr_id] = pr_pattern.findall(text) or [None]
    if pr_id:
        return pr_pattern.sub(github_links.link_to_pr(pr_id), text)
    return text


def generate_changelog():
    from gitchangelog.gitchangelog import main as gitchangelog

    os.environ.setdefault("GITCHANGELOG_CONFIG_FILENAME", GITCHANGELOG_CONFIG_FILENAME)
    gitchangelog()


if __name__ == "__main__":
    logger.info("Generating changelog from GIT")
    generate_changelog()
    logger.info("Done!")
