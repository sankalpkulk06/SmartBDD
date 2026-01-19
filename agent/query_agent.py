import os
import json
from dotenv import load_dotenv
from pinecone import Pinecone
import google.generativeai as genai

# Load API keys
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini setup
genai.configure(api_key=GEMINI_API_KEY)

# Pinecone setup
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

# Function to embed query
def embed_query(text):
    try:
        result = genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type="RETRIEVAL_QUERY"
        )
        return result["embedding"]
    except Exception as e:
        print("Gemini error:", e)
        return None

# Search function
def search(query, top_k=5):
    vector = embed_query(query)
    if not vector:
        print("Failed to generate embedding.")
        return

    results = index.query(vector=vector, top_k=top_k, include_metadata=True)

    print(f"\n🔍 Top {top_k} results for: \"{query}\"\n")
    for match in results['matches']:
        meta = match['metadata']
        print(f"{meta['filename']} (Score: {match['score']:.3f})")
        print(f"→ Summary: {meta['summary']}")
        print("-" * 80)

# Main loop for user input
if __name__ == "__main__":
    while True:
        q = input("\nAsk something (or type 'exit'): ").strip()
        if q.lower() in {"exit", "quit"}:
            break
        search(q)
