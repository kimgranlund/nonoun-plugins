---
id: T-0678
title: "record judges a result by the plugin version that prepared it"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
claimed_by: sdlc-lite-author 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A role dispatched under one plugin version and recorded under a newer one is not closed `failed` only because the result schema changed in between. `prepare` stamps the plugin version on the dispatch and attempt records, and `record` treats a schema failure on an attempt from an older version as a legacy result: recorded `completed` with a `legacy-format` warning, not a failure.

## Intent
- Do: in `prepare` (`plugins/sdlc-lite/scripts/dispatch.py`, the `dispatch = dict(...)` near line 1300 and the `attempt = dict(...)` near line 1323), add `plugin_version` from `plugin_min.running(PLUGIN, 'claude')[0]` to both records. Document the key in the header paragraph on records (near line 95).
- Do: in `record` (same file, the `reason = validate(role, str(result))` branch near line 1776), when the result fails `results.py validate`, the attempt's `plugin_version` is missing or differs from the running version, and the result has at least one `## ` heading, close the attempt `completed` (exit 0) with `legacy_format: <reason>` in the attempt and the `runs.jsonl` line, and print `legacy-format: <role> result <reason>; prepared under <version or "an older plugin">, recorded as completed` on stderr. A failure with a matching version stays exit 3 `failed`. Update the `record` docstring near line 1657 and the record paragraph near line 131.
- Do: add selftest cases: (a) an attempt whose `plugin_version` is rewritten to `0.0.1`, with a result that fails validation (for example a ui-designer review result with `Verdict: pass` but no `## Verdict` section), records with exit 0, `legacy-format` on stderr, and `legacy_format` in the attempt; (b) the same result with the running version exits 3 and the attempt reads `failed`; (c) `prepare` writes `plugin_version` equal to the manifest version in both records.
- Non-goals: shipping old result schemas; teaching `steps.py next` to read a legacy verdict; the stale-scripts stderr warning (T-0679).
- Done when: the criteria pass.

## Context
Source: GitHub issue #33, ui-kit 0.27 vs 0.28 measurement 2026-10-21.
The 0.28.1 `record` rejected `ux0177b-ui-designer-L1`, a review dispatched under 0.27.0 ending `Verdict: pass (0 blocking, 3 advisory)`, with `review mode lacks ## Verdict (pass|pass-with-notes|changes-required)` and closed the attempt `failed`. The conductor then recorded with the pinned 0.27.0 script on purpose. Confirmed on main 8624f984: `grep plugin_version plugins/sdlc-lite/scripts/dispatch.py` finds nothing; the attempt dict near line 1323 has no version key. The rejecting message comes from `_ui_review_error` in `plugins/sdlc-lite/scripts/results.py` near line 311. `plugin_min.running` (`plugins/sdlc-lite/scripts/plugin_min.py` near line 80) already reads the running manifest version.

## Constraints
A result from the current version that fails validation still exits 3 and closes `failed`. A result with no `## ` heading is never accepted as legacy. The existing record selftest cases keep passing.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0 with the new cases, and case (a) fails with the `record` change reverted.
2. `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
3. `git diff --check <base sha>` exits 0.
