"""
Create special redirect files for a documentation's root (/) and for all unmatched routes (non existing pages).
"""
import argparse
import json
import os
import re
from pathlib import Path


def _assert_valid_version(version: str):
    validator = re.compile(r"v\d+\.\d+\.\d+")
    if not validator.match(version):
        raise ValueError(f"Invalid version retrieved '{version}' (valid example 'v1.0.0')")


def _create_redirect_code_snippet(path: str, *, delay_sec: int = 0, custom_code: str = ""):
    return f"""<!DOCTYPE html>
<html>
  <head>
    <title>Redirecting...</title>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="{delay_sec}; url={path}">
    <link rel="canonical" href="https://ibm.github.io/ibm-generative-ai{path}">
    {custom_code}
  </head>
</html>
"""


def create_root_page_redirect(output_directory: Path, version: str):
    _assert_valid_version(version)
    template = _create_redirect_code_snippet(f"/{version}/index.html")
    Path(output_directory, "index.html").write_text(template)


def create_not_found_page_redirect(output_directory: Path, version: str):
    """
    Redirects to the 404 page in the current documentation's version.
    Examples:
        /v2.0.0/non-existing-page -> /v2.0.0/404.html
        /v3.0.0/non-existing-page -> /v3.0.0/404.html
        /some-random-page -> /v3.0.0/404.html  # redirect to the latest version
    """

    _assert_valid_version(version)

    supported_versions = [name for name in os.listdir(output_directory) if os.path.isdir(Path(output_directory, name))]
    if not supported_versions:
        raise RuntimeError("No versions found! Probably wrong path.")

    dynamic_redirect = f"""<script>
    var pathnameParts = window.location.pathname.split('/').slice(1)
    var fallbackVersions = JSON.parse('{json.dumps(supported_versions)}')
    var fallbackVersion = '{version}'

    var currentVersion = pathnameParts.shift()
    if (!fallbackVersions.includes(currentVersion)) {{
        currentVersion = fallbackVersion
    }}

    var target = ['', currentVersion, "404.html"].join('/')
    window.location.href = target
</script>"""

    template = _create_redirect_code_snippet(
        f"/{version}/404.html",
        delay_sec=1,  # give a client time to execute JavaScript
        custom_code=dynamic_redirect,
    )
    Path(output_directory, "404.html").write_text(template)


def _parse_args():
    parser = argparse.ArgumentParser(description="Optional app description")
    parser.add_argument("--version", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    return parser.parse_args()


if __name__ == "__main__":
    config = _parse_args()

    create_root_page_redirect(Path(config.output), config.version)
    create_not_found_page_redirect(Path(config.output), config.version)
