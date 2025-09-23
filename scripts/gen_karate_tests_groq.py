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

import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


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
        return Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"❌ File not found: {path}", file=sys.stderr)
        sys.exit(1)


# --------------------------------------------------------------------------- #
# 3️⃣  Parse oasdiff output
# --------------------------------------------------------------------------- #
def parse_added_endpoints(diff_json: str) -> List[dict]:
    """Return a list of added endpoints from the oasdiff JSON."""
    try:
        diff = json.loads(diff_json)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in diff file: {e}", file=sys.stderr)
        sys.exit(1)

    added = diff.get("added", {})
    endpoints: List[dict] = []

    for path, methods in added.items():
        for method, details in methods.items():
            endpoints.append(
                {
                    "path": path,
                    "method": method.upper(),
                    "summary": details.get("summary") or details.get("description", ""),
                }
            )
    return endpoints


# --------------------------------------------------------------------------- #
# 4️⃣  Build the prompt
# --------------------------------------------------------------------------- #
def build_prompt(spec: str, endpoints: List[dict]) -> str:
    if not endpoints:
        return ""

    endpoint_list = "\n".join(
        f"- `{ep['method']} {ep['path']}`: {ep['summary']}" for ep in endpoints
    )

    prompt = textwrap.dedent(
        f"""
        You are an expert in Karate API testing.
        Here is the full OpenAPI specification of the service:

        ```
        {spec}
        ```

        The following endpoints have just been added:

        {endpoint_list}

        Generate a single Karate `.feature` file that contains:
        • A `Feature:` line with a concise title.
        • One `Scenario:` per new endpoint.
        • The HTTP method, URL and a placeholder for authentication.
        • A 200-299 status-code assertion.
        • Basic body validation – match the top-level keys defined in the response schema.
        • Karate syntax: `* def`, `* match`, etc.

        Output only the contents of the `.feature` file – no surrounding comments.
        """
    )
    return prompt.strip()


# --------------------------------------------------------------------------- #
# 5️⃣  Groq call (with retry)
# --------------------------------------------------------------------------- #

def call_groq(prompt: str, *, verbose: bool = False) -> str:
    _log("[Groq] Sending request…", verbose=verbose)

    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",  # pick your preferred Groq model
            temperature=0.2,
            max_tokens=1500,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that writes Karate tests."},
                {"role": "user", "content": prompt},
            ],
        )
        _log("[Groq] Received response", verbose=verbose)
        return response.choices[0].message.content.strip()


# --------------------------------------------------------------------------- #
# 6️⃣  Main orchestration
# --------------------------------------------------------------------------- #
def main() -> None:
    args = parse_args()

    # 1️⃣ Load spec & diff
    spec = read_file(args.spec)
    diff_json = read_file(args.diff)

    # 2️⃣ Determine added endpoints
    added_endpoints = parse_added_endpoints(diff_json)
    if not added_endpoints:
        print("✅ No new endpoints detected – nothing to generate.", file=sys.stderr)
        sys.exit(0)

    # 3️⃣ Build the LLM prompt
    prompt = build_prompt(spec, added_endpoints)
    if not prompt:
        print("❌ Could not build prompt – aborting.", file=sys.stderr)
        sys.exit(1)

    # 4️⃣ Ask Groq
    try:
        generated = call_groq(prompt, verbose=args.verbose)
    except Exception as e:
        print(f"❌ Groq request failed: {e}", file=sys.stderr)
        sys.exit(1)

    # 5️⃣ Write the feature file (or dry-run)
    output_path = Path(args.out)
    output_path.mkdir(parents=True, exist_ok=True)

    # Unique filename with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    feature_file = output_path / f"auto_generated_{timestamp}.feature"

    if args.dry:
        print(f"\n=== Dry-run: would write to {feature_file} ===\n")
        print(generated)
    else:
        feature_file.write_text(generated, encoding="utf-8")
        print(f"✅ Generated Karate tests → {feature_file}")

    sys.exit(0)


# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    # Ensure the Groq key exists
    if "GROQ_API_KEY" not in os.environ:
        print(
            "❌ GROQ_API_KEY environment variable is missing.\n"
            "     Add it as a secret in your GitHub Actions workflow.",
            file=sys.stderr,
        )
        sys.exit(1)

    main()
