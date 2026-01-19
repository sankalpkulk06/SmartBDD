import json
import re
from pathlib import Path

RAW_PATH = Path("data/raw/test_cases.json")
OUT_PATH = Path("data/processed/test_cases_v1.jsonl")

ANGLE_RE = re.compile(r"<[^>]+>")          # <gender> -> <VAR>
QUOTED_RE = re.compile(r"\"([^\"]*)\"")    # "Bob" -> "VALUE"
WS_RE = re.compile(r"\s+")

def build_canonical_text(summary: str, steps: list[str]) -> str:
    summary = (summary or "").strip()
    steps = steps or []
    steps_block = "\n".join(s.strip() for s in steps if s and s.strip())
    if steps_block:
        return f"{summary}\nSTEPS:\n{steps_block}".strip()
    return summary

def normalize_text(text: str) -> str:
    # 1) normalize <...> placeholders
    text = ANGLE_RE.sub("<VAR>", text)

    # 2) normalize quoted strings
    # keep the quotes so the structure remains, but normalize values inside
    text = QUOTED_RE.sub("\"VALUE\"", text)

    # 3) collapse whitespace
    text = WS_RE.sub(" ", text)

    return text.strip()

def main():
    if not RAW_PATH.exists():
        raise FileNotFoundError(f"Missing raw file: {RAW_PATH}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    data = json.loads(RAW_PATH.read_text(encoding="utf-8"))

    with OUT_PATH.open("w", encoding="utf-8") as f:
        for tc in data:
            tc_id = tc.get("id")
            filename = tc.get("filename")
            steps = tc.get("steps", [])
            summary = tc.get("summary", "")

            canonical = build_canonical_text(summary, steps)
            canonical_norm = normalize_text(canonical)

            out = {
                "id": tc_id,
                "filename": filename,
                "summary": summary,
                "steps": steps,
                "step_count": len(steps) if steps else 0,
                "canonical_text": canonical,
                "canonical_text_normalized": canonical_norm,
                # keep raw gherkin for display/debugging, not embedding
                "gherkin": tc.get("gherkin", ""),
            }

            f.write(json.dumps(out, ensure_ascii=False) + "\n")

    print(f"Wrote: {OUT_PATH} ({len(data)} records)")

if __name__ == "__main__":
    main()