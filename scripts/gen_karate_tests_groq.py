#!/usr/bin/env python3
"""
Generate Karate .feature files from an OpenAPI spec and an oasdiff JSON
using the Groq API (Llama-3.3).

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
from typing import List
from datetime import datetime
import yaml


# ---------------- Argument Parsing ---------------- #
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Karate tests from OpenAPI + oasdiff JSON (Groq)."
    )
    parser.add_argument("--spec", required=True, help="Path to the OpenAPI spec (.yml/.json)")
    parser.add_argument("--diff", required=True, help="Path to the oasdiff JSON file")
    parser.add_argument("--out", required=True, help="Output directory for the .feature file(s)")
    parser.add_argument("--dry", action="store_true", help="Do not write files – just print output")
    parser.add_argument("--verbose", action="store_true", help="Print debug information")
    parser.add_argument("--prompt-file", help="Path to prompt template text file")
    return parser.parse_args()


# ---------------- Utility Helpers ---------------- #
def _log(msg: str, *, verbose: bool) -> None:
    if verbose:
        print(msg, file=sys.stderr)


def read_file(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"❌ File not found: {path}", file=sys.stderr)
        sys.exit(1)


# ---------------- Parse oasdiff output ---------------- #
def parse_added_endpoints(diff_json: str, spec_yaml: dict) -> list:
    diff = json.loads(diff_json)

    if isinstance(diff, dict):
        added_paths = diff.get("added") or diff.get("extensions", {}).get("added", [])
    elif isinstance(diff, list):
        added_paths = diff
    else:
        added_paths = []

    endpoints = []
    for path in added_paths:
        method = "GET"  # default if unknown
        summary = ""
        # Try to get summary from spec.yaml
        try:
            if "paths" in spec_yaml and path in spec_yaml["paths"]:
                method = list(spec_yaml["paths"][path].keys())[0]
                summary = spec_yaml["paths"][path][method].get("summary", "")
        except Exception:
            pass
        endpoints.append({
            "path": path,
            "method": method.upper(),
            "summary": summary
        })
    return endpoints


# ---------------- Build the Prompt ---------------- #
def build_prompt(spec_str: str, endpoint: dict, prompt_template: str = None) -> str:
    endpoint_list = f"- `{endpoint['method']} {endpoint['path']}`: {endpoint.get('summary', '')}"

    if prompt_template:
        base_prompt = prompt_template
    else:
        base_prompt = textwrap.dedent("""
            You are an expert in Karate API testing.
            Here is the full OpenAPI specification of the service:

            ```
            {spec_str}
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
        """)

    return base_prompt.format(spec_str=spec_str, endpoint_list=endpoint_list)


# ---------------- Filename Generator ---------------- #
def make_feature_filename(endpoint: dict) -> str:
    if endpoint.get("summary"):
        name = endpoint["summary"].strip().lower().replace(" ", "-").replace("/", "")
    else:
        name = f"{endpoint.get('method', 'get').lower()}-{endpoint.get('path', '').replace('/', '-')}"
    return f"{name}.feature"


# ---------------- Groq Call ---------------- #
def call_groq(prompt: str, *, verbose: bool = False) -> str:
    _log("[Groq] Sending request…", verbose=verbose)
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.2,
        max_tokens=1500,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that writes Karate tests."},
            {"role": "user", "content": prompt},
        ],
    )
    _log("[Groq] Received response", verbose=verbose)
    return response.choices[0].message.content.strip()


# ---------------- Main Orchestration ---------------- #
def main() -> None:
    args = parse_args()

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

    prompt_template = None
    if args.prompt_file:
        prompt_template = read_file(args.prompt_file)

    output_path = Path(args.out)
    output_path.mkdir(parents=True, exist_ok=True)

    for endpoint in added_endpoints:
        prompt = build_prompt(spec_str, endpoint, prompt_template)
        print("\n=== Generated Prompt for endpoint:", endpoint['path'], "===\n")
        print(prompt)

        if not args.dry:
            try:
                generated = call_groq(prompt, verbose=args.verbose)
            except Exception as e:
                print(f"❌ Groq request failed for {endpoint['path']}: {e}", file=sys.stderr)
                continue

            filename = make_feature_filename(endpoint)
            feature_file = output_path / filename
            feature_file.write_text(generated, encoding="utf-8")
            print(f"✅ Generated {feature_file}")


# ---------------- Entry Point ---------------- #
if __name__ == "__main__":
    if "GROQ_API_KEY" not in os.environ:
        print("❌ GROQ_API_KEY environment variable is missing.", file=sys.stderr)
        sys.exit(1)
    main()
