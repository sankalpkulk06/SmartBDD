# Retrieval Spec (SmartBDD) - v1

## 1) Goal
SmartBDD helps QA teams **search** and **deduplicate** Cucumber BDD test cases using semantic similarity.
This spec defines:
- what a retrievable "unit" is
- which fields represent the **meaning** of a unit (embedded)
- which fields are **metadata** (filtering/debugging)
- what query types the system must support

This prevents embedding inconsistent fields and makes evaluation reproducible.

---

## 2) Retrieval Unit (What one vector represents)
**Retrieval unit:** one test case record (one `TC-XXX` entry in `data/raw/test_cases.json`).

Each unit corresponds to a single scenario/scenario-outline test case and includes:
- `id` (unique identifier)
- `filename` (source `.feature` file)
- `steps` (normalized list of step strings)
- `summary` (short intent statement)
- `gherkin` (raw feature text, for display/debugging)

**Why**
- Keeps indexing and evaluation consistent: 1 test case == 1 vector == 1 search result item.
- Avoids mixing granularities (per-step vs per-scenario vs per-file) in v1.

---

## 3) Meaning Fields (What we embed) - v1
### Embedded fields
We embed a single `canonical_text` constructed from:
1) `summary` (captures intent in 1 line)
2) `steps` (captures behavioral sequence)

**Rationale**
- `summary` answers: what is the test validating?
- `steps` answers: what actions/assertions define the flow?
- Together they best represent “duplicate-ness” for BDD tests.

### Not embedded in v1
- `gherkin` (too noisy: formatting, Examples tables, repeated boilerplate)
- `filename` (not semantic; use as metadata only)

**Note**
Raw `gherkin` is kept for UI display and debugging, not as the primary embedding input.

---

## 4) Canonical Text Definition
We will create per test case:
- `canonical_text`:
  - `summary`
  - newline
  - `STEPS:` header
  - each step on its own line

Example structure:
- Summary: `Verifies login fails with incorrect password`
- Steps:
  - `Given ...`
  - `When ...`
  - `Then ...`

We will also create:
- `canonical_text_normalized` (see normalization section below)

---

## 5) Normalization Policy (for dedupe and stable similarity)
Goal: reduce superficial differences while preserving meaning.

v1 normalization rules:
1) Replace any placeholder like `<gender>`, `<mail>`, `<password>` with `<VAR>`
2) Replace quoted string values `"something"` with `"VALUE"` (optional, but recommended for dedupe)
3) Collapse whitespace and trim
4) Preserve step keywords `Given/When/Then/And` to keep structure

**Tradeoff**
- Too little normalization => misses duplicates (false negatives)
- Too much normalization => merges unrelated tests (false positives)

We will iterate normalization rules based on eval failures.

---

## 6) Metadata Fields (stored alongside vectors)
These fields are stored for filtering, grouping, and debugging:
- `id`
- `filename`
- `step_count` (len(steps))
- `feature_name` (optional: parsed from `Feature:` line)
- `scenario_name` (optional: parsed from `Scenario:` / `Scenario Outline:` line)

**Why**
- Enables precise filtering and reduces false positives:
  - filter by feature/module
  - compare within a domain (account creation, cart, checkout)

---

## 7) Query Types to Support (v1)
The system must support these query types:

1) **Natural language search**
Example: `tests for invalid email format`

2) **Find duplicates / near-duplicates of a given test case**
Input: `TC-001` (or its canonical_text)
Output: top-k similar test cases

3) **Find closest scenario based on step snippets**
Input: a few steps copied from a feature file
Output: nearest matching test case(s)

---

## 8) Evaluation Targets (v1)
We will evaluate retrieval + dedupe decisions using:
- Retrieval: `Recall@k`, `Precision@k`, `MRR` (once labels exist)
- Dedupe decision: false merge rate (critical), precision/recall on labeled pairs

Eval datasets will live in `data/eval/` and be versioned (`*_v1.jsonl`, `*_v2.jsonl`).

---

## 9) Versioning
This spec is **v1**.
If we change meaning fields, normalization, or unit definition, we bump the spec version and regenerate:
- `data/processed/test_cases_v{n}.jsonl`
- `data/eval/eval_pairs_v{n}.jsonl`