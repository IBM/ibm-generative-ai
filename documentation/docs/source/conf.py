# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

sys.path.insert(0, os.path.abspath("../../../src/genai"))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "IBM Generative AI Python SDK"
copyright = "2023, IBM Research"
author = "IBM Research"

# -- General configuration ---------------------------------ß------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
    "sphinx.ext.autosectionlabel",
]

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
# html_theme = "alabaster"
html_static_path = ["_static"]
html_title = "GENAI Python SDK API Docs"
html_theme_options = {
    "light_css_variables": {
        "font-stack": "'IBM Plex Sans', -apple-system, BlinkMacSystemFont, Segoe UI, Arial, sans-serif",
        "font-stack--monospace": "'IBM Plex Mono', 'SFMono-Regular', Menlo, Consolas, Lucida Console, monospace",
    }
}
html_css_files = ["custom.css"]
