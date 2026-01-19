# scripts/v1/rule_judge_v1.py
#
# Rule-based judge for SmartBDD duplicate detection.
# v1.1: uses stronger intent fingerprint (action/page/product/intent keywords),
# avoids using weak "Then anchor overlap" as a dup signal.
#
# Usage:
#   python scripts/v1/rule_judge_v1.py

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

TESTS_PATH = Path("data/processed/test_cases_v1.jsonl")
EVAL_PATH = Path("data/eval/eval_pairs_v1.jsonl")

WS_RE = re.compile(r"\s+")

PAGE_RE = re.compile(r'on the "([^"]+)" page', re.IGNORECASE)
PRODUCT_RE = re.compile(r'navigate to product "([^"]+)"', re.IGNORECASE)
CATEGORY_RE = re.compile(r'navigate to category "([^"]+)"', re.IGNORECASE)
CUSTOMIZE_RE = re.compile(r'customize with message', re.IGNORECASE)
ADD_TO_CART_RE = re.compile(r'\badd to cart\b', re.IGNORECASE)

FIELD_RE = re.compile(
    r"associated with the field\s+(?:\"([^\"]+)\"|<([^>]+)>|([^\n]+))",
    re.IGNORECASE,
)

# High-signal outcome anchors
DISABLED_SUBMIT_RE = re.compile(r"submit order button should be disabled", re.IGNORECASE)
WARNING_RE = re.compile(r"warning message", re.IGNORECASE)
ORDER_PLACED_RE = re.compile(r"order should be placed", re.IGNORECASE)
CUSTOM_MSG_SHOULD_BE_RE = re.compile(r"customized message should be", re.IGNORECASE)
ERROR_FLOW_RE = re.compile(r"error message|should still be on the", re.IGNORECASE)

# Very small intent keywords from summary/filename (cheap, high value for templated steps)
INTENT_KEYWORDS = [
    "invalid email",
    "email format",
    "password too short",
    "privacy",
    "gdpr",
    "incorrect password",
    "exceeds stock",
    "quantity",
    "remove",
    "customized message",
    "too long",
    "sale conditions",
    "logged-in",
    "logged-out",
    "two products",
    "create an account",
    "modify",
]


def read_jsonl(path: Path) -> List[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def normalize_text(s: str) -> str:
    s = (s or "").strip().lower()
    s = WS_RE.sub(" ", s)
    return s


def normalize_gherkin(gherkin: str) -> str:
    return normalize_text(gherkin)


def extract_field_token(text: str) -> Optional[str]:
    m = FIELD_RE.search(text or "")
    if not m:
        return None
    token = m.group(1) or m.group(2) or m.group(3)
    if token is None:
        return None
    token = token.strip().strip('"').strip()
    token = WS_RE.sub(" ", token)
    return token


def infer_action(text: str) -> Optional[str]:
    t = (text or "").lower()

    if "fill accountcreation fields" in t:
        return "account_creation"
    if "fill myidentity fields" in t:
        return "account_modify"
    if "initiate order placement process" in t:
        return "checkout"
    if ADD_TO_CART_RE.search(t) and "navigate to product" in t:
        return "add_to_cart"
    if "update product quantities" in t or "update quantity to" in t:
        return "update_quantity"
    if "remove product" in t:
        return "remove_product"
    if "log in with email" in t or 'on the "login" page' in t:
        return "login"
    return None


def extract_outcome_anchor(text: str) -> Optional[str]:
    """
    Returns a high-signal outcome anchor category.
    """
    if DISABLED_SUBMIT_RE.search(text):
        return "disabled_submit"
    if ORDER_PLACED_RE.search(text):
        return "order_placed"
    if WARNING_RE.search(text):
        return "warning"
    if CUSTOM_MSG_SHOULD_BE_RE.search(text):
        return "custom_msg_should_be"
    if ERROR_FLOW_RE.search(text):
        return "error_flow"
    return None


def extract_intent_keywords(summary: str, filename: str) -> List[str]:
    blob = normalize_text(summary) + " " + normalize_text(filename)
    hits = []
    for kw in INTENT_KEYWORDS:
        if kw in blob:
            hits.append(kw)
    return hits


def extract_signals(tc: dict) -> Dict[str, Optional[object]]:
    steps = tc.get("steps", []) or []
    text = "\n".join(steps)

    pages = PAGE_RE.findall(text)
    page = pages[-1] if pages else None

    products = PRODUCT_RE.findall(text)
    product = products[-1] if products else None

    categories = CATEGORY_RE.findall(text)
    category = categories[-1] if categories else None

    field = extract_field_token(text)
    action = infer_action(text)

    has_customize = bool(CUSTOMIZE_RE.search(text))
    add_to_cart_count = len(ADD_TO_CART_RE.findall(text))

    outcome_anchor = extract_outcome_anchor(text)

    gherkin_norm = normalize_gherkin(tc.get("gherkin", ""))

    summary = tc.get("summary", "") or ""
    filename = tc.get("filename", "") or ""
    intent_kws = extract_intent_keywords(summary, filename)

    return {
        "page": page,
        "field": field,
        "action": action,
        "product": product,
        "category": category,
        "has_customize": has_customize,
        "add_to_cart_count": add_to_cart_count,
        "outcome_anchor": outcome_anchor,
        "gherkin_norm": gherkin_norm,
        "intent_kws": intent_kws,
        "summary": summary,
        "filename": filename,
    }


def share_any(a: List[str], b: List[str]) -> bool:
    return bool(set(a or []).intersection(set(b or [])))


def rule_decide(a_sig: Dict[str, Optional[object]], b_sig: Dict[str, Optional[object]]) -> str:
    """
    dup / not_dup / unknown

    Key change:
    - Do NOT use generic Then anchor overlap as a dup rule.
    - Require matching fingerprints: (action, page, product/outcome/intent).
    """
    # 1) Exact copy shortcut
    if a_sig.get("gherkin_norm") and a_sig["gherkin_norm"] == b_sig.get("gherkin_norm"):
        return "dup"

    # 2) Hard not-dup mismatches
    if a_sig.get("action") and b_sig.get("action") and a_sig["action"] != b_sig["action"]:
        return "not_dup"

    if a_sig.get("page") and b_sig.get("page") and a_sig["page"] != b_sig["page"]:
        return "not_dup"

    # Cart-specific: customization presence mismatch => not dup
    if a_sig.get("action") == "add_to_cart" and b_sig.get("action") == "add_to_cart":
        if bool(a_sig.get("has_customize")) != bool(b_sig.get("has_customize")):
            return "not_dup"

        # Different product names => not dup (for these datasets)
        if a_sig.get("product") and b_sig.get("product") and a_sig["product"] != b_sig["product"]:
            return "not_dup"

        # Add-to-cart count differs significantly (1 vs 2 products scenario)
        if a_sig.get("add_to_cart_count") and b_sig.get("add_to_cart_count"):
            if a_sig["add_to_cart_count"] != b_sig["add_to_cart_count"]:
                return "not_dup"

    # Error field mismatch if both known
    if a_sig.get("field") and b_sig.get("field") and a_sig["field"] != b_sig["field"]:
        return "not_dup"

    # Outcome anchor mismatch if both known and not generic error_flow
    a_out, b_out = a_sig.get("outcome_anchor"), b_sig.get("outcome_anchor")
    if a_out and b_out and a_out != b_out:
        # example: cart_should_contain vs customized_message_should_be gets caught here
        return "not_dup"

    # 3) Conservative dup rule:
    # Require action+page match (if present) AND strong shared intent:
    # - same product OR
    # - shared intent keywords OR
    # - same specific outcome anchor (not just generic error_flow)
    action_ok = (not a_sig.get("action") or not b_sig.get("action") or a_sig["action"] == b_sig["action"])
    page_ok = (not a_sig.get("page") or not b_sig.get("page") or a_sig["page"] == b_sig["page"])

    if action_ok and page_ok:
        same_product = bool(a_sig.get("product") and b_sig.get("product") and a_sig["product"] == b_sig["product"])
        shared_intent = share_any(a_sig.get("intent_kws", []), b_sig.get("intent_kws", []))
        same_outcome = bool(a_out and b_out and a_out == b_out and a_out != "error_flow")

        if same_product or shared_intent or same_outcome:
            return "dup"

    return "unknown"


def main():
    tests_list = read_jsonl(TESTS_PATH)
    tests = {r["id"]: r for r in tests_list}
    evals = read_jsonl(EVAL_PATH)

    sig: Dict[str, Dict[str, Optional[object]]] = {}
    for tc_id, tc in tests.items():
        sig[tc_id] = extract_signals(tc)

    total = len(evals)
    decided = 0
    correct = 0

    tp = fp = fn = 0
    unknowns: List[Tuple[str, str, str, str]] = []
    false_positives: List[Tuple[str, str, str]] = []
    false_negatives: List[Tuple[str, str, str]] = []

    for e in evals:
        a, b, gold = e["a"], e["b"], e["label"]
        pred = rule_decide(sig[a], sig[b])

        if pred == "unknown":
            unknowns.append((a, b, gold, e.get("reason", "")))
            continue

        decided += 1
        if pred == gold:
            correct += 1
        else:
            if pred == "dup" and gold != "dup":
                false_positives.append((a, b, e.get("reason", "")))
            if pred != "dup" and gold == "dup":
                false_negatives.append((a, b, e.get("reason", "")))

        if pred == "dup":
            if gold == "dup":
                tp += 1
            else:
                fp += 1
        else:
            if gold == "dup":
                fn += 1

    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0

    print("=== Rule Judge v1.1 (Fingerprint) ===")
    print(f"Total eval pairs: {total}")
    print(f"Decided (not unknown): {decided}")
    print(f"Unknown: {len(unknowns)}")
    if decided:
        print(f"Accuracy on decided: {correct / decided:.3f}")
    print()
    print(f"Dup precision: {prec:.3f}  (tp={tp}, fp={fp})")
    print(f"Dup recall:    {rec:.3f}  (tp={tp}, fn={fn})")
    print()

    if false_positives:
        print("False positives (pred dup, gold not_dup):")
        for a, b, reason in false_positives[:10]:
            print(f"  FP: {a} -> {b} | {reason}")
        print()

    if false_negatives:
        print("False negatives (pred not_dup, gold dup):")
        for a, b, reason in false_negatives[:10]:
            print(f"  FN: {a} -> {b} | {reason}")
        print()

    print("Unknown examples (first 10):")
    for a, b, gold, reason in unknowns[:10]:
        print(f"  {a} -> {b} gold={gold} | {reason}")

    if unknowns:
        print()
        print("Debug signals for first 5 unknowns:")
        for a, b, gold, _ in unknowns[:5]:
            print(f"- {a} vs {b} (gold={gold})")
            print("  A:", {k: sig[a][k] for k in ["action","page","product","has_customize","add_to_cart_count","outcome_anchor","intent_kws"]})
            print("  B:", {k: sig[b][k] for k in ["action","page","product","has_customize","add_to_cart_count","outcome_anchor","intent_kws"]})


if __name__ == "__main__":
    main()