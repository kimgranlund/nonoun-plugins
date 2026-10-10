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
- Do: the `verify: needed` line is written by the solo agent from plugins/sdlc-lite/agents/solo.md (levels L2 and L3 text), not by a script. Add one new script `scripts/verify_scope.py <base>` with a function `docs_only(paths)` and a CLI that reads `git diff --name-only <base>` (plus untracked files) and exits 0 and prints `docs-only` when every changed path is under `docs/`, or under `.sdlc/` and a record file (not scripts), or a `*.md` file outside `plugins/*/agents` and `plugins/*/skills`, and `docs_check.py` plus the link check exit 0; otherwise it exits 1 and prints the first path that is not docs-only. Change agents/solo.md (then run claude_roles.py and codex_roles.py generate): after the checks pass, run `verify_scope.py <base sha>`; on exit 0 end with `verify: skipped (docs/records only; docs_check green)` instead of `verify: needed`; any other result keeps `verify: needed`. `tickets.py close` accepts a ticket without a verifier result only when `verify_scope.docs_only` agrees for that ticket's diff against its recorded base; otherwise it still requires one. A `verifier: L1`..`L3` line in the handoff overrides the skip (the author wants one).
- Non-goals: skipping the verifier for any code, skill, agent or hook change; model or effort changes.
- Done when:
  - Selftest cases, each observed failing first: a docs-only diff prints the skipped line and `tickets.py close` accepts it; a diff touching one script path prints `verify: needed` and close refuses without a verifier; a skill or agent file that is Markdown still needs a verifier; a record-only diff that fails docs_check still needs one.
  - verify_scope.py, tickets.py and dispatch.py selftests, claude_roles.py and codex_roles.py generate --check, check.py and tickets.py check pass.

## Context
Maintainer decision 2026-10-10: no verifier for docs, records and reports only. Evidence: verifier minutes 43 to 56 each and one verifier per ticket even for docs-only changes (ultimate-tokens, maison retros 2026-10-09, 2026-10-10). The other two skip rules chosen the same day (mechanical template instances, never re-verifying a pass) are in T-0427.

## Constraints
No em or en dashes. No push or publish. Model and effort defaults are the maintainer's: change none. Independent verification at ticket close stays; this ticket removes layers above it, not that verifier.
