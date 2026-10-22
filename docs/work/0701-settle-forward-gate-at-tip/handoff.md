---
id: T-0701
title: "settle --forward says when it skipped its gates"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-21
claimed_by: sdlc-lite-author 2026-10-21
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`fanout.py settle --forward --gate <cmd>` never moves main past a commit no gate ran on without saying so.

## Intent
- Do: in `plugins/sdlc-lite/scripts/fanout.py` `settle_forward`, when main is already in the integration branch (no forward merge) and `--gate` was given, run the gates at the integration tip under the gate lock before fast-forwarding, unless the gate ledger already holds a pass for that tip sha; when it does, print `settle: gates already passed at <sha7>`. A gate failure stops before main moves.
- Non-goals: changing `--catch-up`.
- Done when: the criteria pass.

## Context
Issue: GitHub #44 (machine-wide concurrency, 2026-10-21: six lanes plus Codex and a second conductor drove an 18-core Mac to load 128; all load came from test runners). "`fanout.py settle --forward` fast-forwarded main without running `--gate`. The integration branch already contained main, so there was nothing to forward-merge. The last commit, a merge of main into the integration branch, therefore has no gate-ledger entry."

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0 with a new case: an integration branch that already contains main, settled with `--gate "false"`, exits non-zero and main does not move; with `--gate "true"` it fast-forwards. The case fails with the change reverted.
2. `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
3. `git diff --check <base sha>` exits 0.
