import os
import re
import textwrap

import yaml
from _common.logger import get_logger
from dotenv import load_dotenv
from tabulate import tabulate

from docs_changelog_generator.config import ChangelogConfig, DefaultChangelogConfig, config_context_var
from docs_changelog_generator.utils import (
    GithubRSTLinks,
    get_git_tags,
    output_engine_pipeline,
    shave_marks,
    use_context,
)
from genai._generated.endpoints import ApiEndpoint

load_dotenv()

logger = get_logger(__name__)


@output_engine_pipeline
def inject_versions(data, opts, _config):
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
def inject_author_usernames(data, opts, config: ChangelogConfig):
    github_links = GithubRSTLinks(config.repo_url)

    with open(config.author_names_mapping_path) as f:
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
                    logger.warn(f'Author "{author}" not found in {config.author_names_mapping_path}')
                    resolved_author_names.append(author)
                else:
                    resolved_author_names.append(github_links.link_to_user(author_names_map[author_shaved]))
            commit["author_names_resolved"] = ", ".join(resolved_author_names)
    return data, opts


@output_engine_pipeline
def inject_compare_link(data, opts, config):
    github_links = GithubRSTLinks(config.repo_url)

    if not isinstance(data["versions"], list):
        data["versions"] = list(data["versions"])

    tags = get_git_tags()

    for version in data["versions"]:
        if version["tag"] is None:
            link = github_links.link_to_compare(tags[-1].identifier, "HEAD")  # latest ... HEAD
        else:
            version_index = tags.index(version["tag"])
            link = github_links.link_to_compare(tags[version_index].identifier, tags[version_index - 1].identifier)
        version["full_changelog_link"] = f"**Full Changelog**: {link}"
    return data, opts


def subject_process(text):
    config = config_context_var.get()
    github_links = GithubRSTLinks(config.repo_url)

    pr_pattern = re.compile(r"\(#([0-9]+)\)$")
    [pr_id] = pr_pattern.findall(text) or [None]
    if pr_id:
        return pr_pattern.sub(github_links.link_to_pr(pr_id), text)
    return text


def generate_changelog(config: ChangelogConfig):
    from gitchangelog.gitchangelog import main as gitchangelog

    os.environ.setdefault("GITCHANGELOG_CONFIG_FILENAME", str(config.gitchangelog_config_path))

    with use_context(config_context_var, config):
        gitchangelog()  # parses cmd arguments


if __name__ == "__main__":
    logger.info("Generating changelog from GIT")
    generate_changelog(DefaultChangelogConfig)
    logger.info("Done!")
