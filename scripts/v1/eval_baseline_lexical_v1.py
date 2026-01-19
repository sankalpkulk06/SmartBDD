import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional

CANDIDATES_PATH = Path("data/processed/candidates_lexical_v1.jsonl")
EVAL_PAIRS_PATH = Path("data/eval/eval_pairs_v1.jsonl")

# Evaluate multiple k values so you can see the curve
K_VALUES = [1, 3, 5, 10]

def read_jsonl(path: Path) -> List[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows

def load_candidates(path: Path) -> Dict[str, List[dict]]:
    """
    Returns: {id: [{"id": neighbor_id, "score": float}, ...]}
    """
    rows = read_jsonl(path)
    mapping = {}
    for r in rows:
        mapping[r["id"]] = r.get("neighbors", [])
    return mapping

def rank_of_target(neighbors: List[dict], target_id: str) -> Optional[Tuple[int, float]]:
    """
    If target_id is in neighbors, return (1-based rank, score). Otherwise None.
    """
    for idx, n in enumerate(neighbors):
        if n.get("id") == target_id:
            return (idx + 1, float(n.get("score", 0.0)))
    return None

def safe_get(mapping: Dict[str, List[dict]], key: str) -> List[dict]:
    return mapping.get(key, [])

def main():
    if not CANDIDATES_PATH.exists():
        raise FileNotFoundError(f"Missing candidates file: {CANDIDATES_PATH}")
    if not EVAL_PAIRS_PATH.exists():
        raise FileNotFoundError(f"Missing eval pairs file: {EVAL_PAIRS_PATH}")

    candidates = load_candidates(CANDIDATES_PATH)
    pairs = read_jsonl(EVAL_PAIRS_PATH)

    # Split pairs
    dup_pairs = [p for p in pairs if p.get("label") == "dup"]
    neg_pairs = [p for p in pairs if p.get("label") == "not_dup"]

    # Collect per-pair results
    dup_results = []
    neg_results = []

    for p in dup_pairs:
        a, b = p["a"], p["b"]
        neighbors = safe_get(candidates, a)
        hit = rank_of_target(neighbors, b)
        dup_results.append((p, hit))

    for p in neg_pairs:
        a, b = p["a"], p["b"]
        neighbors = safe_get(candidates, a)
        hit = rank_of_target(neighbors, b)
        neg_results.append((p, hit))

    # Print summary
    print("=== Baseline Evaluation: Lexical Candidates (TF-IDF) ===")
    print(f"Pairs: total={len(pairs)} dup={len(dup_pairs)} not_dup={len(neg_pairs)}")
    print()

    # Recall@k and MRR for dup pairs
    if len(dup_pairs) > 0:
        print("Dup metrics:")
        for k in K_VALUES:
            hits = 0
            for _, hit in dup_results:
                if hit is not None and hit[0] <= k:
                    hits += 1
            recall = hits / len(dup_pairs)
            print(f"  Recall@{k}: {hits}/{len(dup_pairs)} = {recall:.3f}")

        # MRR: average of 1/rank for hits, 0 if not found
        rr_sum = 0.0
        for _, hit in dup_results:
            rr_sum += (1.0 / hit[0]) if hit is not None else 0.0
        mrr = rr_sum / len(dup_pairs)
        print(f"  MRR: {mrr:.3f}")
        print()
    else:
        print("Dup metrics: (no dup pairs found)")
        print()

    # False-alarm@k for not_dup pairs
    if len(neg_pairs) > 0:
        print("Not-dup risk (negatives appearing in top-k):")
        for k in K_VALUES:
            false_hits = 0
            for _, hit in neg_results:
                if hit is not None and hit[0] <= k:
                    false_hits += 1
            rate = false_hits / len(neg_pairs)
            print(f"  FalseAlarm@{k}: {false_hits}/{len(neg_pairs)} = {rate:.3f}")
        print()
    else:
        print("Not-dup risk: (no not_dup pairs found)")
        print()

    # Print failures (dup not found) and dangerous negatives (not_dup found at high rank)
    print("Top dup misses (dup pairs where b was NOT retrieved):")
    misses = [(p, hit) for (p, hit) in dup_results if hit is None]
    for p, _ in misses[:10]:
        print(f"  MISS dup: {p['a']} -> {p['b']} | reason: {p.get('reason','')}")
    if not misses:
        print("  (none)")
    print()

    print("Most dangerous negatives (not_dup pairs retrieved in top-3):")
    dangerous = []
    for p, hit in neg_results:
        if hit is not None and hit[0] <= 3:
            dangerous.append((hit[0], hit[1], p))
    dangerous.sort(key=lambda x: (x[0], -x[1]))
    for rank, score, p in dangerous[:10]:
        print(f"  DANGER not_dup: {p['a']} -> {p['b']} at rank={rank} score={score} | {p.get('reason','')}")
    if not dangerous:
        print("  (none)")
    print()

    # Optional: show ranks for all dup pairs
    print("Dup pair ranks:")
    for p, hit in dup_results:
        if hit is None:
            print(f"  {p['a']} -> {p['b']}: NOT FOUND")
        else:
            print(f"  {p['a']} -> {p['b']}: rank={hit[0]} score={hit[1]}")

if __name__ == "__main__":
    main()