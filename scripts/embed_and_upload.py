import json
import os
from dotenv import load_dotenv
from pinecone import Pinecone
import google.generativeai as genai

# Load environment variables
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

def get_embedding(text):
    try:
        result = genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type="RETRIEVAL_DOCUMENT"
        )
        return result["embedding"]
    except Exception as e:
        print("Gemini error:", e)
        return None

# Connect to Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

# Load test cases
with open(os.path.join("..", "data", "test_cases.json"), "r", encoding="utf-8") as f:
    test_cases = json.load(f)

# Upload batch
batch = []
for case in test_cases:
    emb = get_embedding(case["summary"])
    if emb:
        batch.append({
            "id": case["id"],
            "values": emb,
            "metadata": {
                "filename": case["filename"],
                "summary": case["summary"],
                "steps": case["steps"]
            }
        })

# Push to Pinecone
if batch:
    index.upsert(batch)
    print(f"Uploaded {len(batch)} test cases to Pinecone.")
else:
    print("No valid embeddings to upload.")
