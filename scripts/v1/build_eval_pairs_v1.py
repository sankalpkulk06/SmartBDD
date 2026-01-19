#!/usr/bin/env python3
"""
Build data/eval/eval_pairs_v1.jsonl from data/raw (test_cases.json and .feature files).

Labels are curated from manual analysis of each test case's intent, steps, and source:
- dup: same scenario/flow and same acceptance criteria (true duplicate or merge-safe).
- not_dup: different intent, different validation, or different flow.

All pairs use TC-ids from data/raw/test_cases.json. Pairs are ordered (a, b) with a < b
for consistency; one direction per pair to avoid redundant (a,b) and (b,a).
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
EVAL = ROOT / "data" / "eval"


def load_test_cases() -> list[dict]:
    with (RAW / "test_cases.json").open() as f:
        return json.load(f)


def get_ids(tcs: list[dict]) -> set[str]:
    return {t["id"] for t in tcs}


# Curated pairs: (a, b) with a < b, and (label, reason).
# Derived from data/raw/test_cases.json and .feature files.
CURATED_PAIRS: list[tuple[str, str, str, str]] = [
    # --- dup: true duplicates (same steps, same intent) ---
    (
        "TC-010",
        "TC-011",
        "dup",
        "Exact duplicate: same feature and scenario. TC-010 from '... (1).feature' and TC-011 from '...feature'; identical steps (add customizable product with message to cart, Mug personnalisable, Joyeux anniversaire) and intent.",
    ),
    (
        "TC-007",
        "TC-020",
        "dup",
        "Exact duplicate: TC-020 is a copied feature file of TC-007 (log in with correct credentials). Same steps, same assertions, same intent.",
    ),
    (
        "TC-015",
        "TC-021",
        "dup",
        "Exact duplicate: TC-021 copies the cart quantity update scenario from TC-015 with identical steps and expected totals.",
    ),
    (
        "TC-017",
        "TC-022",
        "dup",
        "Exact duplicate: TC-022 is a copy of TC-017 (cannot place order without sales conditions). Same checkout steps and disabled submit assertion.",
    ),
    # --- not_dup: same high-level flow pattern but different validation/assertion ---
    (
        "TC-001",
        "TC-002",
        "not_dup",
        "Account creation fails: invalid email vs password too short. Same 4-step pattern (AccountCreation, fill+submit, stay, error on field) but different field and acceptance criteria.",
    ),
    (
        "TC-001",
        "TC-003",
        "not_dup",
        "Account creation fails: invalid email vs privacy/GDPR not checked. Same structure, different validation (email_txt vs privacy_cb/gdpr_cb).",
    ),
    (
        "TC-002",
        "TC-003",
        "not_dup",
        "Account creation fails: password too short vs privacy/GDPR not checked. Same flow, different fields and rules.",
    ),
    (
        "TC-003",
        "TC-005",
        "not_dup",
        "Privacy/GDPR: account creation fails vs account modification fails. Same rule, different context (AccountCreation vs MyIdentity) and steps.",
    ),
    # --- not_dup: login success vs failure ---
    (
        "TC-007",
        "TC-008",
        "not_dup",
        "Login: success with correct credentials vs failure with incorrect password. Same preconditions and Login page; opposite outcomes and assertions.",
    ),
    # --- not_dup: cart – add product variants ---
    (
        "TC-009",
        "TC-010",
        "not_dup",
        "Add to cart: one product (no customization, logged in) vs one product with customized message (logged out). Different product type, customization step, and login state.",
    ),
    (
        "TC-010",
        "TC-014",
        "not_dup",
        "Both use Mug personnalisable and customize: TC-010 adds to cart successfully; TC-014 asserts message truncation when too long. Different intent and Then clause.",
    ),
    (
        "TC-009",
        "TC-012",
        "not_dup",
        "Add one product vs add two products to cart. Different scenario (single vs multiple products).",
    ),
    # --- not_dup: cart – update vs remove ---
    (
        "TC-015",
        "TC-016",
        "not_dup",
        "Cart: update product quantities vs remove a product. Both modify cart contents; different action and assertion.",
    ),
    # --- not_dup: order placement ---
    (
        "TC-017",
        "TC-018",
        "not_dup",
        "Order: cannot place when sales conditions not approved vs place order when approved. Same checkout flow up to approveSalesConditions; opposite choice and outcome.",
    ),
    (
        "TC-018",
        "TC-019",
        "not_dup",
        "Place order: logged-in customer vs logged-out (login during checkout). Different entry state and steps (e.g. fill login form in TC-019).",
    ),
    # --- not_dup: account success flows ---
    (
        "TC-004",
        "TC-006",
        "not_dup",
        "Create account vs modify account. Both succeed; different flow (creation+login vs MyIdentity update) and assertion.",
    ),
    # --- not_dup: cross-domain (account vs cart vs order) ---
    (
        "TC-001",
        "TC-017",
        "not_dup",
        "Account creation fail (invalid email) vs cannot place order (sales conditions). Different domain and flow.",
    ),
    (
        "TC-004",
        "TC-009",
        "not_dup",
        "Create account vs add one product to cart. Different domain.",
    ),
    (
        "TC-012",
        "TC-014",
        "not_dup",
        "Add two products to cart vs customized message too long. Different intents and flows.",
    ),
]


def _norm(s: str) -> str:
    return " ".join(s.split()) if isinstance(s, str) else str(s)


def main() -> None:
    tcs = load_test_cases()
    ids = get_ids(tcs)

    # Validate and normalize: ensure a < b and ids exist
    seen = set()
    out: list[dict] = []
    for t in CURATED_PAIRS:
        if len(t) == 4:
            a, b, label, reason = t
        else:
            raise ValueError(f"Invalid tuple: {t}")
        if a not in ids or b not in ids:
            raise ValueError(f"Unknown id in pair: {a!r}, {b!r}. Known: {sorted(ids)}")
        key = (a, b) if a < b else (b, a)
        if key in seen:
            continue
        seen.add(key)
        aa, bb = (a, b) if a < b else (b, a)
        out.append({"a": aa, "b": bb, "label": label, "reason": _norm(reason)})

    EVAL.mkdir(parents=True, exist_ok=True)
    p = EVAL / "eval_pairs_v1.jsonl"
    with p.open("w") as f:
        for rec in out:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Wrote {len(out)} pairs to {p}")


if __name__ == "__main__":
    main()
