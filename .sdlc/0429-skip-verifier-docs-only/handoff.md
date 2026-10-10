---
id: T-0429
title: "No verifier for a ticket that changes only docs, records or reports"
type: feature        # feature | bug | chore | spike | idea
status: ready
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-10
claimed_by: claude 2026-10-10
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A ticket whose diff touches only docs, records or reports closes on its own checks, with no verifier run, and the report says so.

## Intent
- Do: in scripts/solo_run.py the solo completion report prints `verify: needed` for levels L2 and L3 (and the conductor then prepares a verifier). Add a decision from the actual diff against the recorded base: when every changed path is under `docs/`, `.sdlc/` (records only, not scripts), or a `*.md` file outside `plugins/*/agents` and `plugins/*/skills`, and docs_check.py plus the link check exit 0, print `verify: skipped (docs/records only; docs_check green)` instead and record `verifier: skipped` with the reason in the runs row. Any other path, including a skill, agent, script, hook or manifest, keeps `verify: needed`. Make the path rule one function that steps.py (lane choice) and tickets.py close can call; tickets.py close accepts a skipped verifier only when that function agrees, else it still requires a verifier result. A `--force-verify` flag on solo_run keeps the old behavior.
- Non-goals: skipping the verifier for any code, skill, agent or hook change; model or effort changes.
- Done when:
  - Selftest cases, each observed failing first: a docs-only diff prints the skipped line and `tickets.py close` accepts it; a diff touching one script path prints `verify: needed` and close refuses without a verifier; a skill or agent file that is Markdown still needs a verifier; a record-only diff that fails docs_check still needs one.
  - solo_run.py, tickets.py, steps.py and dispatch.py selftests, check.py and tickets.py check pass.

## Context
Maintainer decision 2026-10-10: no verifier for docs, records and reports only. Evidence: verifier minutes 43 to 56 each and one verifier per ticket even for docs-only changes (ultimate-tokens, maison retros 2026-10-09, 2026-10-10). The other two skip rules chosen the same day (mechanical template instances, never re-verifying a pass) are in T-0427.

## Constraints
No em or en dashes. No push or publish. Model and effort defaults are the maintainer's: change none. Independent verification at ticket close stays; this ticket removes layers above it, not that verifier.
