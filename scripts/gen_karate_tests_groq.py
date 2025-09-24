#!/usr/bin/env python3
"""
Generate Karate .feature files from an OpenAPI spec and an oasdiff JSON
using the Groq API (Llama-3.1).

Usage:
    python scripts/gen_karate_tests_groq.py \
        --spec ./openapi/base.yml \
        --diff ./api_diff.json \
        --out ./tests/auto_generated \
        [--dry] [--verbose] [--prompt-file ./scripts/prompt.txt]

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
from typing import List, Dict
from datetime import datetime
import yaml


# --------------------------------------------------------------------------- #
# Argument parsing
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
    parser.add_argument(
        "--prompt-file",
        help="Path to a saved prompt base text file to prepend before spec and endpoints"
    )
    return parser.parse_args()


# --------------------------------------------------------------------------- #
# Utility helpers
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
# Parse oasdiff output
# --------------------------------------------------------------------------- #
def parse_added_endpoints(diff_json: str, spec_yaml: dict) -> list:
    diff = json.loads(diff_json)
    if isinstance(diff, dict):
        added_paths = diff.get("added") or diff.get("extensions", {}).get("added", [])
    elif isinstance(diff, list):
        added_paths = diff
    else:
        added_paths = []

    endpoints = []
    for path_info in added_paths:
        path_str = path_info if isinstance(path_info, str) else path_info.get("path", "")
        method = "GET"
        summary = ""

        if isinstance(path_info, dict):
            method = path_info.get("method", "GET")

        if path_str in spec_yaml.get("paths", {}):
            path_methods = spec_yaml["paths"][path_str]
            if method.lower() in path_methods:
                summary = path_methods[method.lower()].get("summary", "")

        endpoints.append({
            "path": path_str,
            "method": method,
            "summary": summary
        })

    return endpoints


# --------------------------------------------------------------------------- #
# Group endpoints by base path
# --------------------------------------------------------------------------- #
def group_endpoints(endpoints: List[dict]) -> Dict[str, List[dict]]:
    grouped = {}
    for ep in endpoints:
        base_path = ep["path"].split("{")[0].rstrip("/")
        if base_path not in grouped:
            grouped[base_path] = []
        grouped[base_path].append(ep)
    return grouped


# --------------------------------------------------------------------------- #
# Build the prompt
# --------------------------------------------------------------------------- #
def build_prompt(spec_str: str, endpoints: List[dict], base_prompt: str = "") -> str:
    endpoint_list = "\n".join(
        f"- `{ep['method']} {ep['path']}`: {ep['summary']}" for ep in endpoints
    )

    extra_text = textwrap.dedent(
        f"""
        Here is the full OpenAPI specification of the service:

        ```
        {spec_str}
        ```

        The following endpoints have just been added:

        {endpoint_list}
        """
    )

    return f"{base_prompt}\n{extra_text}".strip()


# --------------------------------------------------------------------------- #
# Call Groq API
# --------------------------------------------------------------------------- #
def call_groq(prompt: str, *, verbose: bool = False) -> str:
    _log("[Groq] Sending request…", verbose=verbose)
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.2,
        max_tokens=2000,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that writes Karate tests."},
            {"role": "user", "content": prompt},
        ],
    )
    _log("[Groq] Received response", verbose=verbose)
    return response.choices[0].message.content.strip()


# --------------------------------------------------------------------------- #
# Main orchestration
# --------------------------------------------------------------------------- #
def main() -> None:
    args = parse_args()

    base_prompt = ""
    if args.prompt_file:
        base_prompt = read_file(args.prompt_file)

    spec_str = read_file(args.spec)
    try:
        spec_yaml = yaml.safe_load(spec_str)
    except yaml.YAMLError as e:
        print(f"❌ Failed to parse YAML: {e}", file=sys.stderr)
        sys.exit(1)

    diff_json = read_file(args.diff)
    added_endpoints = parse_added_endpoints(diff_json, spec_yaml)

    if not added_endpoints:
        print("✅ No new endpoints detected – nothing to generate.", file=sys.stderr)
        sys.exit(0)

    grouped = group_endpoints(added_endpoints)
    output_path = Path(args.out)
    output_path.mkdir(parents=True, exist_ok=True)

    for base_path, endpoints in grouped.items():
        prompt = build_prompt(spec_str, endpoints, base_prompt)
        if not prompt:
            print("❌ Could not build prompt – aborting.", file=sys.stderr)
            sys.exit(1)

        print("\n=== Generated Prompt ===\n")
        print(prompt)
        print("\n=== End of Prompt ===\n")

        try:
            generated = call_groq(prompt, verbose=args.verbose)
        except Exception as e:
            print(f"❌ Groq request failed: {e}", file=sys.stderr)
            sys.exit(1)

        filename = f"{base_path.strip('/').replace('/', '-') or 'root'}.feature"
        feature_file = output_path / filename

        if args.dry:
            print(f"\n=== Dry-run: would write to {feature_file} ===\n")
            print(generated)
        else:
            feature_file.write_text(generated, encoding="utf-8")
            print(f"✅ Generated Karate tests → {feature_file}")


# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    if "GROQ_API_KEY" not in os.environ:
        print(
            "❌ GROQ_API_KEY environment variable is missing.\n"
            "     Add it as a secret in your GitHub Actions workflow.",
            file=sys.stderr,
        )
        sys.exit(1)
    main()
