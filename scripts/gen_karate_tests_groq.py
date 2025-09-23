#!/usr/bin/env python3
"""
Generate Karate .feature files from an OpenAPI spec and an oasdiff JSON
using the Groq API (Llama‑3.3).

Usage:
    python scripts/gen_karate_tests_groq.py \
        --spec ./openapi/base.yml \
        --diff ./api_diff.json \
        --out ./tests/auto_generated \
        [--dry] [--verbose]

Environment:
    GROQ_API_KEY   - your Groq API key
"""

import argparse
import os
import json
import yaml
from groq import Groq

# --------------------------------------------------------------------------- #
# Argument parsing
# --------------------------------------------------------------------------- #
def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate Karate tests from OpenAPI + oasdiff JSON (Groq)."
    )
    parser.add_argument("--spec", required=True, help="Path to the OpenAPI spec (.yml/.json)")
    parser.add_argument("--diff", required=True, help="Path to the oasdiff JSON file")
    parser.add_argument("--out", required=True, help="Output directory for the .feature file")
    parser.add_argument("--dry", action="store_true", help="Print generated tests instead of writing file")
    parser.add_argument("--verbose", action="store_true", help="Print debug information")
    return parser.parse_args()


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def read_yaml(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def read_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def log(msg, verbose=False):
    if verbose:
        print(msg)


# --------------------------------------------------------------------------- #
# Build prompt for Groq
# --------------------------------------------------------------------------- #
def build_prompt(spec, diff):
    """
    Create a prompt for Groq to generate Karate tests
    """
    changed_paths = []

    # Extract changed endpoints from diff
    for breaking in diff.get("breakingChanges", []):
        path = breaking.get("path")
        if path and path not in changed_paths:
            changed_paths.append(path)

    # If no diff info, just cover everything
    if not changed_paths:
        changed_paths = list(spec.get("paths", {}).keys())

    paths_subset = {p: spec["paths"][p] for p in changed_paths}

    prompt = (
        "You are an expert in Karate DSL API testing.\n"
        "Given the OpenAPI spec and a diff of newly added or changed APIs, generate a Karate test suite.\n\n"
        "Rules:\n"
        "- Use Karate DSL (.feature file) syntax\n"
        "- Cover at least one positive test for each new/changed endpoint\n"
        "- Add placeholders for request bodies and expected responses\n"
        "- Keep it simple and readable\n\n"
        f"OpenAPI Paths:\n{json.dumps(paths_subset, indent=2)}\n\n"
        "Return only the Karate test content."
    )

    return prompt


# --------------------------------------------------------------------------- #
# Call Groq API
# --------------------------------------------------------------------------- #
def call_groq(prompt, verbose=False):
    log("[Groq] Sending request...", verbose)
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # updated model
        temperature=0.3,
        messages=[
            {"role": "system", "content": "You are a helpful assistant for test automation."},
            {"role": "user", "content": prompt},
        ],
    )
    log("[Groq] Received response", verbose)
    return response.choices[0].message.content


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main():
    args = parse_args()

    # Ensure Groq key exists
    if "GROQ_API_KEY" not in os.environ:
        print("❌ GROQ_API_KEY environment variable is missing.", file=os.stderr)
        exit(1)

    # Load spec & diff
    spec = read_yaml(args.spec)
    diff = read_json(args.diff)

    # Build prompt
    prompt = build_prompt(spec, diff)
    if not prompt:
        print("❌ Could not build prompt – aborting.", file=os.stderr)
        exit(1)

    # Generate Karate tests
    try:
        karate_tests = call_groq(prompt, verbose=args.verbose)
    except Exception as e:
        print(f"❌ Groq request failed: {e}", file=os.stderr)
        exit(1)

    # Dry-run: print tests
    if args.dry:
        print("\n=== Generated Karate Tests ===\n")
        print(karate_tests)
    else:
        os.makedirs(args.out, exist_ok=True)
        out_file = os.path.join(args.out, "auto_generated.feature")
        with open(out_file, "w") as f:
            f.write(karate_tests)
        print(f"✅ Karate tests written to {out_file}")


if __name__ == "__main__":
    main()
