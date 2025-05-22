import os
import json

# paths relative to the project root
input_folder = os.path.join("..", "data", "test_cases")
output_file = os.path.join("..", "data", "test_cases.json")

def read_gherkin_file(file_path):
    # Read the Gherkin file and return its content
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def extract_steps(gherkin_text):
    # Extract steps from the Gherkin text
    steps = []
    for line in gherkin_text.splitlines():
        line = line.strip()
        # Only include lines that start with Gherkin keywords
        # (Given, When, Then, And, But)
        if line.startswith(("Given", "When", "Then", "And", "But")):
            steps.append(line)
    return steps

test_cases = []
feature_files = [f for f in os.listdir(input_folder) if f.endswith(".feature")]

for i, file_name in enumerate(feature_files):
    full_path = os.path.join(input_folder, file_name)
    gherkin_text = read_gherkin_file(full_path)
    test_cases.append({
        "id": f"TC-{i+1:03d}",
        "filename": file_name,
        "gherkin": gherkin_text,
        "steps": extract_steps(gherkin_text),
        "summary": ""  # To be filled later
    })

# Save to JSON
with open(output_file, "w", encoding='utf-8') as out:
    json.dump(test_cases, out, indent=2)

print(f"Created {output_file} with {len(test_cases)} test cases.")
