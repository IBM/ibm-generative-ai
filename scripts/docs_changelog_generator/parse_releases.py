import re
from datetime import datetime

import m2r
import requests

from docs_changelog_generator.config import OUTPUT_FILE


def _parse_github_releases() -> list[str]:
    """Function to parse github release notes, if that's ever needed again."""
    releases = requests.get("https://api.github.com/repos/ibm/ibm-generative-ai/releases").json()

    result = ["Changelog", "=========", "\n"]
    for release in releases:
        name = (
            release["name"].replace("Release ", "")
            + f" ({datetime.fromisoformat(release['published_at']).strftime('%Y-%m-%d')})"
        )
        result += [name]
        result += ["-" * len(name)]

        class MyRenderer(m2r.RestRenderer):
            hmarks = {1: "^", 2: "^", 3: "^", 4: "^", 5: "^", 6: "^"}

        body_pre_convert = release["body"]
        # Remove "What's changed" header
        body_pre_convert = re.sub(r"#+\s*What'?s? [Cc]hanged\s*\n", "", body_pre_convert)

        # Convert MD to RST
        body_converted = m2r.convert(body_pre_convert, renderer=MyRenderer())

        # Convert compare links
        body_converted = re.sub(
            r"https://github.com/IBM/ibm-generative-ai/compare/v([0-9]\.[0-9]\.[0-9])...v([0-9]\.[0-9]\.[0-9])",
            "`v\\1...v\\2 <https://github.com/IBM/ibm-generative-ai/compare/v\\1...v\\2>`_",
            body_converted,
        )

        # Convert PR links
        body_converted = re.sub(
            "https://github.com/IBM/ibm-generative-ai/pull/([0-9]*)",
            "`#\\1 <https://github.com/IBM/ibm-generative-ai/pull/\\1>`_",
            body_converted,
        )

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
    changelog = _parse_github_releases()
    with open(OUTPUT_FILE, "w") as f:
        f.writelines(changelog)
