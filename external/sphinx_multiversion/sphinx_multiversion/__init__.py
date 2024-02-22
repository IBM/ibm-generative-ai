# This file contains code modified from the 'sphinx-multiversion' project
# Original author: Jan Holthuis
# The original code is licensed under the BSD 2-Clause "Simplified" License.

# -*- coding: utf-8 -*-
from .main import main
from .sphinx import setup

__version__ = "0.2.4"

__all__ = [
    "setup",
    "main",
]
