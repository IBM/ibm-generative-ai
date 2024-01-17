import re
from datetime import datetime

import m2r
import requests

from docs_changelog_generator.config import ChangelogConfig, DefaultChangelogConfig
from docs_changelog_generator.utils import GithubRSTLinks


def parse_github_releases(config: ChangelogConfig) -> list[str]:
    """Function to parse github release notes, if that's ever needed again."""
    releases = requests.get(f"{config.repo_api_url}/releases").json()
    github_links = GithubRSTLinks(config.repo_url)

    result = ["Changelog", "=========", "\n"]
    for release in releases:
        name = (
            release["name"].replace("Release ", "")
            + f" ({datetime.fromisoformat(release['published_at']).strftime('%Y-%m-%d')})"
        )
        result += [name]
        result += ["-" * len(name)]

        class MyRenderer(m2r.RestRenderer):
            hmarks = {1: "^", 2: "^", 3: "^", 4: "^", 5: "^", 6: "^"}  # unify all headings to the same level

        body_pre_convert = release["body"]
        # Remove "What's changed" header
        body_pre_convert = re.sub(r"#+\s*What'?s? [Cc]hanged\s*\n", "", body_pre_convert)

        # Convert MD to RST
        body_converted = m2r.convert(body_pre_convert, renderer=MyRenderer())

        # Convert compare links
        body_converted = re.sub(
            rf"{config.repo_url}/compare/(v[0-9]\.[0-9]\.[0-9])...(v[0-9]\.[0-9]\.[0-9])",
            github_links.link_to_compare("\\1", "\\2"),
            body_converted,
        )
        # Convert PR links
        body_converted = re.sub(rf"{config.repo_url}/pull/([0-9]*)", github_links.link_to_pr("\\1"), body_converted)
        # Convert User links
        body_converted = re.sub(r"@(\S+)", github_links.link_to_user("\\1"), body_converted)

        # Convert emojis
        body_converted = (
            body_converted.replace(r"\ :", ":")
            .replace(":bug:", "🐛")
            .replace(":hammer:", "🔨")
            .replace(":sparkles:", "✨")
            .replace(":wrench:", "🔧")
            .replace(":art:", "🎨")
            .replace(":rocket:", "🚀")
        )
        result += [body_converted, ""]
    return [f"{line}\n" for line in result]


if __name__ == "__main__":
    config = DefaultChangelogConfig
    changelog = parse_github_releases(config)
    with open(config.output_file_path, "w") as f:
        f.writelines(changelog)
