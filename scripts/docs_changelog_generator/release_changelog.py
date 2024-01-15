import argparse
import re
from datetime import datetime

import dateutil.utils
import packaging.version
from _common.logger import get_logger
from dotenv import load_dotenv

from docs_changelog_generator.config import OUTPUT_FILE, unreleased_version_label
from docs_changelog_generator.utils import GithubRSTLinks, get_git_tags

load_dotenv()
logger = get_logger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument("version", help="New version tag to release")
parser.add_argument(
    "--date",
    required=False,
    type=datetime.fromisoformat,
    help="Optional date of the release YYYY-MM-DD, today by default",
    default=dateutil.utils.today(),
)
args = parser.parse_args()
github_links = GithubRSTLinks()
unreleased_version_regex = r"""(?isxu)
(
    %(unreleased_version_label)s\s*(\n|\r\n|\r)      ## ``(unreleased)`` line
    --+(\n|\r\n|\r)                                  ## ``---`` underline
)
""" % {"unreleased_version_label": re.escape(unreleased_version_label)}


def release_changelog():
    new_version = args.version
    if not re.match(r"^v[0-9]\.[0-9]\.[0-9]$", new_version):
        raise ValueError(r"Version must satisfy the pattern ^v[0-9]\.[0-9]\.[0-9]$")

    latest_tag = get_git_tags()[-1].identifier
    version_tuple = packaging.version.parse(new_version.lstrip("v"))
    latest_tag_tuple = packaging.version.parse(latest_tag.lstrip("v"))
    if version_tuple <= latest_tag_tuple:
        raise ValueError(f"Version must be higher than the latest version: {latest_tag}")

    header = f'{new_version} ({args.date.strftime("%Y-%m-%d")})'
    logger.info(f"Change {unreleased_version_label} -> {header}")
    header += f'\n{"-" * len(header)}\n'

    with open(OUTPUT_FILE, "r") as f:
        changelog = f.read()

    if not re.findall(unreleased_version_regex, changelog):
        raise ValueError("No unreleased version found")

    changelog = re.sub(unreleased_version_regex, header, changelog, count=1)
    changelog = changelog.replace(
        github_links.link_to_compare(latest_tag, "HEAD"),
        github_links.link_to_compare(latest_tag, new_version),
        1,
    )

    with open(OUTPUT_FILE, "w") as f:
        f.write(changelog)
    logger.info("OK")


if __name__ == "__main__":
    logger.info("Updating changelog for release")
    release_changelog()
    logger.info("Done!")
