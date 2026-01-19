import json
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

IN_PATH = Path("data/processed/test_cases_v1.jsonl")
OUT_PATH = Path("data/processed/candidates_lexical_v1.jsonl")

TOP_K = 10  # adjust to 10-30

def read_jsonl(path: Path):
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows

def main():
    rows = read_jsonl(IN_PATH)
    ids = [r["id"] for r in rows]

    # Use normalized canonical text for lexical baseline
    texts = [r.get("canonical_text", "") for r in rows]

    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    X = vec.fit_transform(texts)

    sims = cosine_similarity(X, X)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUT_PATH.open("w", encoding="utf-8") as out:
        for i, tc_id in enumerate(ids):
            # sort neighbors by similarity, skip itself
            scored = [(j, float(sims[i, j])) for j in range(len(ids)) if j != i]
            scored.sort(key=lambda x: x[1], reverse=True)

            neighbors = [
                {"id": ids[j], "score": round(score, 6)}
                for j, score in scored[:TOP_K]
            ]

            out_row = {"id": tc_id, "neighbors": neighbors}
            out.write(json.dumps(out_row, ensure_ascii=False) + "\n")

    print(f"Wrote: {OUT_PATH} ({len(ids)} rows, top_k={TOP_K})")

if __name__ == "__main__":
    main()