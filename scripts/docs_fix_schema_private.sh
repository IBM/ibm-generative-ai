#!/bin/bash
# Add :imported-members: under :members: into genai.schema package documentation
# We want to keep _api.py as a private module
set -e

dir=$(dirname "$0")
imported_members=":imported-members:"

output="$(sed "s/:members:/:members:\n   ${imported_members}/" "${dir}/../documentation/source/rst_source/genai.schema.rst")"
echo "$output" > documentation/source/rst_source/genai.schema.rst
