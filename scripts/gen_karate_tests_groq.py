#!/usr/bin/env python3
import argparse
import os
import json
import yaml
from groq import Groq

TEMPLATE_PROMPT = """
You are an expert in Karate DSL API testing.
Given the OpenAPI spec and a diff of newly added or changed APIs, generate a Karate test suite.

Rules:
- Use Karate DSL (.feature file) syntax
- Cover at least one positive test for each new/changed endpoint
- Add placeholders for request bodies and expected responses
- Keep it simple and readable

Return only the Karate test content.
"""

def load_yaml(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def main():
    parser = argparse.ArgumentParser(description="Generate Karate tests using Groq LLM")
    parser.add_argument("--spec", required=True, help="Path to OpenAPI spec (YAML)")
    parser.add_argument("--diff", required=True, help="Path to API diff JSON")
    parser.add_argument("--out", required=True, help="Output folder for Karate tests")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)

    # Load inputs
    spec = load_yaml(args.spec)
    diff = load_json(args.diff)

    # Extract changed endpoints from diff
    changed_paths = []
    if diff:
        for breaking in diff.get("breakingChanges", []):
            path = breaking.get("path")
            if path and path not in changed_paths:
                changed_paths.append(path)

    # If no diff info, just cover everything
    if not changed_paths:
        changed_paths = list(spec.get("paths", {}).keys())

    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    # Prepare prompt
    prompt = TEMPLATE_PROMPT + "\n\nOpenAPI Paths:\n" + json.dumps(
        {p: spec["paths"][p] for p in changed_paths}, indent=2
    )

    print("🔍 Sending prompt to Groq for test generation...")

    response = client.chat.completions.create(
        model="llama3-70b-8192",  # good balance between reasoning & generation
        messages=[
            {"role": "system", "content": "You are a helpful assistant for test automation."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )

    karate_tests = response.choices[0].message.content

    out_file = os.path.join(args.out, "auto_generated.feature")
    with open(out_file, "w") as f:
        f.write(karate_tests)

    print(f"✅ Karate tests written to {out_file}")


if __name__ == "__main__":
    main()
