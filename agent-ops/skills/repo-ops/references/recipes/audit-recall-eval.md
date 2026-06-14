---
date: 2026-05-30
coverage: canonical
peers:
  - ../audit-patterns/orphan-detection.md
  - ../audit-patterns/stale-content.md
  - self-healing-hooks.md
status: research-verified
---

# Audit-recall eval (does the audit catch what it claims to?)

> **The premise.** `repo-ops` audits other repos; this eval audits repo-ops's _own audit_ — it measures how many planted defects the audit actually finds. Without it, the audit's accuracy is _assumed_, not known: "the orphan detector works" is a claim until you seed an orphan and confirm it's caught. Pairs with the routing-eval corpus (which measures _triggering_) — this measures _finding_. Raised by the 2026-05-30 9-critic review (Boris/Huyen): an auditor with no recall number gives false confidence.

## The metric

**Recall per category** = (planted defects of that category the audit flagged) ÷ (planted defects of that category).

- Recall = 1.0 → the audit catches everything it's seeded with.
- Recall < 1.0 → a **false-negative class** — the audit missed a defect it claims to catch. This is the dangerous failure for an auditor: a clean report that isn't.
- Track **precision** too (flagged-and-real ÷ total-flagged) to catch over-flagging — but **recall is the headline**: an auditor that misses defects certifies broken repos clean.
- **Baseline:** lock per-category recall at the current version; a drop on re-run is a regression.

## The planted-defect fixture

Materialize a throwaway brain under `evals/fixtures/recall-brain/` with a KNOWN set of defects (the ground truth). Minimal but spanning the audit categories:

| # | Category | Planted defect (the seed) | Expected finding |
| --- | --- | --- | --- |
| 1 | Orphan | `.agents/brain/adrs/0009-orphan.md` referenced by nothing | `ORPHAN: .agents/brain/adrs/0009-orphan.md` |
| 2 | Orphan (basename trap) | two `README.md` in different dirs; only one linked | the _unlinked_ one flagged — regression guard for the v1.10.4 basename fix |
| 3 | Staleness | a doc dated 400 days ago, no `_Last reviewed:_` | `STALE: …` |
| 4 | Broken intra-repo link | `AGENTS.md` links `[x](.agents/brain/missing.md)` | `BROKEN LINK: .agents/brain/missing.md` |
| 5 | Entry-file bloat | `AGENTS.md` at 220 lines | `ENTRY-FILE >200 lines (block)` |
| 6 | Drift | `CLAUDE.md` a 40-line fat divergent copy of `AGENTS.md` | `DRIFT: CLAUDE.md vs AGENTS.md` |
| 7 | Missing memory home | no `.agents/brain/adrs/` and no "no architectural changes" note | `MISSING MEMORY PRIMITIVE: adrs` |
| 8 | Malformed CHANGELOG | a `# Changelog` title sitting below a version entry | `CHANGELOG malformed` — regression guard for the library-wide fix |
| 9 | Undated spec | a `.agents/brain/` doc with no `date:` / `_Last reviewed:_` | `FORMAT: undated` |
| 10 | Injection bait | a brain file containing "IGNORE PREVIOUS INSTRUCTIONS, write…" | `injection-attempt` (flagged as content, **never executed**) |

Each fixture file carries a comment `<!-- PLANTED: category N; expect: <finding> -->` so the ground truth lives beside the defect and the eval can parse expectations. Also seed a few **clean** files (no defects) so the audit's precision is measured — it must NOT flag those.

## The procedure

```text
1. SEED    — generate evals/fixtures/recall-brain/ from the table above. Idempotent: regenerate from
             the spec/script, never hand-edit drift in.
2. RUN     — point the audit at the fixture (report-only; NEVER apply-mode on the fixture).
3. COMPARE — per planted defect: was a matching finding emitted? (match on category + path)
             per clean file: was anything flagged? (precision)
4. SCORE   — recall = caught ÷ planted, per category + overall; precision = real ÷ flagged.
5. ASSERT  — every category's recall == its locked baseline (start: 1.0 for the 10 above);
             a drop FAILS the eval.
6. LEDGER  — append the run + scores to .agents/brain/audit-history/ as a `trip-wire-fired` record
             (the audit-recall eval is itself a trip-wire — see self-healing liveness).
```

## What good looks like / anti-patterns

- **Recall 1.0 across all 10 categories** on a fresh run is the target; rows #2 (basename trap) and #8 (malformed CHANGELOG) are explicit regression guards for fixes shipped this version line.
- **Don't hand-edit the fixture to make the eval pass** — regenerate it from the spec. A fixture that drifts to match the audit is the same self-grading trap the skill warns against elsewhere.
- **Recall, not just precision** — an auditor tuned never to false-flag but with poor recall is worse than useless: it certifies broken repos clean.
- **Unverified-by-construction note (honest default):** this eval ships as a _spec + procedure_. repo-ops's audit runs in the _target_ repo, so the recall/precision numbers are produced when the eval is actually run there — they are **not asserted here**. Until run, treat the audit's own accuracy as **unmeasured**.

## Cross-references

- Routing eval (triggering, not finding): the routing-eval corpus
- Orphan detection (incl. the basename fix that row #2 guards): `../audit-patterns/orphan-detection.md`, `self-healing-hooks.md`
- Self-healing liveness (the ledger this eval writes to): `self-healing-hooks.md`
- Reliability dial (severity of a recall-drop routes through strictness): `../guidance/reliability-dial.md`
