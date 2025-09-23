#!/usr/bin/env python3
"""
Generate Karate .feature files from an OpenAPI spec and an oasdiff JSON
using the Groq API (Llama‑3.3).

Usage:
    python scripts/gen_karate_tests_groq.py \
        --spec ./openapi/base.yml \
        --diff ./api_diff.json \
        --out ./tests/auto_generated \
        [--verbose]

Environment:
    GROQ_API_KEY   - your Groq API key
"""

import argparse
import os
import sys
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
# Build prompt for Groq
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
        print("❌ GROQ_API_KEY environment variable is missing.", file=sys.stderr)
        exit(1)

    # Load spec & diff
    spec = read_yaml(args.spec)
    diff = read_json(args.diff)

    # Build prompt
    prompt = build_prompt(spec, diff)
    if not prompt:
        print("❌ Could not build prompt – aborting.", file=sys.stderr)
        exit(1)

    # Generate Karate tests
    try:
        karate_tests = call_groq(prompt, verbose=args.verbose)
    except Exception as e:
        print(f"❌ Groq request failed: {e}", file=sys.stderr)
        exit(1)

    # Print the generated tests
    print("\n=== Generated Karate Tests ===\n")
    print(karate_tests)

    # Write to file
    # Unique filename with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    os.makedirs(args.out, exist_ok=True)
    out_file = os.path.join(args.out, f"auto_generated_{timestamp}.feature")
    with open(out_file, "w") as f:
        f.write(karate_tests)
    print(f"\n✅ Karate tests written to {out_file}")


if __name__ == "__main__":
    main()