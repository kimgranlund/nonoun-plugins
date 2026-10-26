---
date: 2026-10-16
slug: project-reconciliation
requested_by: user
harness: Codex desktop
authors:
  - role: solo
    agent: Codex
    model: not recorded
    did: reconciled installed and project skills, repaired lookup compatibility, ran both suites and benchmark
project: context-fog-of-war-map
verification: automated tests and unchanged benchmark passed; no independent verifier
backup: /Users/kimba/Projects/context-fog-of-war-map/artifacts/reconcile-20261016
---

## Added
- `tests/test_reconciliation.py`: three regressions for legacy arguments, generic errors on plain readers, and preservation of benign triage.
- Restored project `scripts/triage.py` alongside the installed runtime-harness additions.

## Changed
- Preserved installed learnings, contract audit, projections, bundle reconstruction, token-cap detector, local tests, viewer reference and historical change logs.
- Merged triage into `scripts/diagnostics.py`, `references/session.schema.json`, `references/diagnostics.md` and `SKILL.md`.
- Retained project benchmark v2 and CLI triage, and advanced `engineer.py` analyzerVersion to 6.

## Fixed
- `diagnostics.py`: parse legacy command strings and nested arguments using the lookup parser. Attribute an exact generic missing-file error only to a plain single-file reader. Compound, multi-file, redirected and variable-based commands retain conservative matching.
- Initial project suite exposed six failures/errors after the first merge; both suites pass after compatibility repair: project 143, skill 49. Frozen benchmark scores unchanged, including triaged problem precision 0.85 and recall 1.0.

## Open
- Three benchmark nonproblem candidates still lack intent/exclusion evidence; preserved as needs-review.
- Benchmark fixtures do not evaluate the new static audit or stop-at-cap detector; those are covered by skill-local regressions, not production reliability claims.
- No new live workflow outcome experiment was run.
