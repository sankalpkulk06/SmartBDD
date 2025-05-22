import openai
import os
import json
import time
from dotenv import load_dotenv

# Load .env variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set OpenAI client (new v1 )
client = openai.OpenAI()

# File paths
input_file = os.path.join("..", "data", "test_cases.json")
output_file = os.path.join("..", "data", "test_cases_with_summaries.json")

def get_summary(gherkin_text):
    # Generate a summary for the given Gherkin text using OpenAI API
    prompt = f"Summarize the following Gherkin scenario in one sentence:\n\n{gherkin_text}"
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a QA engineer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        summary = response.choices[0].message.content.strip()
        print(f"Summary: {summary}\n")
        return summary
    except Exception as e:
        print("Error generating summary:\n", e)
        return ""

# Load input test cases
with open(input_file, "r", encoding="utf-8") as f:
    test_cases = json.load(f)

# Generate summaries
for case in test_cases:
    if not case.get("summary"):
        print(f"Summarizing {case['id']}...")
        case["summary"] = get_summary(case["gherkin"])
        time.sleep(1)  # avoid hitting rate limits

# Save output with summaries
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(test_cases, f, indent=2)

print(f"All summaries written to: {output_file}")
