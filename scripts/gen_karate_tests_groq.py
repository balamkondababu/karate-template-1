#!/usr/bin/env python3
"""
Generate Karate .feature files from an OpenAPI spec and an oasdiff JSON
using the Groq API (Llama-3.1).

Usage:
    python scripts/gen_karate_tests_groq.py \
        --spec ./openapi/base.yml \
        --diff ./api_diff.json \
        --out  ./tests/auto_generated \
        [--dry] [--verbose]

Environment:
    GROQ_API_KEY   - your Groq API key
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import textwrap
from pathlib import Path
from typing import List
from datetime import datetime


# --------------------------------------------------------------------------- #
# 1️⃣  Argument parsing
# --------------------------------------------------------------------------- #
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Karate tests from OpenAPI + oasdiff JSON (Groq)."
    )
    parser.add_argument("--spec", required=True, help="Path to the OpenAPI spec (.yml/.json)")
    parser.add_argument("--diff", required=True, help="Path to the oasdiff JSON file")
    parser.add_argument("--out", required=True, help="Output directory for the .feature file")
    parser.add_argument("--dry", action="store_true", help="Do not write files – just print what would be written")
    parser.add_argument("--verbose", action="store_true", help="Print debug information")
    return parser.parse_args()


# --------------------------------------------------------------------------- #
# 2️⃣  Utility helpers
# --------------------------------------------------------------------------- #
def _log(msg: str, *, verbose: bool) -> None:
    if verbose:
        print(msg, file=sys.stderr)


def read_file(path: str) -> str:
    try:
        return P
