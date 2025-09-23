import openai, sys, argparse, json, os

parser = argparse.ArgumentParser()
parser.add_argument("--spec", required=True)
parser.add_argument("--diff", required=True)
parser.add_argument("--out", required=True)
args = parser.parse_args()

with open(args.spec) as f: spec = f.read()
with open(args.diff) as f: diff = f.read()

prompt = f"""
You are an expert in Karate API testing.
Here is the OpenAPI spec:
{spec}

The new endpoints introduced are:
{diff}

Generate Karate .feature tests with basic validations.
"""

resp = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}]
)

os.makedirs(args.out, exist_ok=True)
with open(os.path.join(args.out, "auto_generated.feature"), "w") as f:
    f.write(resp["choices"][0]["message"]["content"])
