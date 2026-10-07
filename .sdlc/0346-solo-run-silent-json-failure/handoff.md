---
id: T-0346
title: "solo_run.py run prints a clear error when its stream is unreadable instead of exiting silently on a JSON parse failure"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0342]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-07
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
solo_run.py run prints a clear error when its stream is unreadable instead of exiting silently on a JSON parse failure

## Intent
- Do: With stderr sent to /dev/null, solo_run.py run exits silently with a JSON parse failure (maison). Print the failure and the raw first line to stdout (not only stderr) and exit non-zero with the log path; selftest with a malformed stream line. First reproduce the reported behavior (the report is a conductor's account, marked [U]); if it cannot be reproduced on the current main, close with a note saying so instead of changing code.
- Non-goals: model or effort changes; anything outside the named script or hook.
- Done when:
  - a selftest feeds a malformed JSON line and sees a non-zero exit plus a message on stdout naming the log path. (observed, failing on the old behavior).
  - check.py, tickets.py check and the touched selftests pass.

## Context
From the maison conductor's upstream friction list of 2026-10-07 (about 40 sub-agent runs, no verification by me yet). Start after T-0342, which edits the same scripts and hook.

## Constraints
No em or en dashes. No push or publish.
