---
id: T-0298
title: "429 limit marker records the reset time"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
When a 429 or session-limit log prints a reset time (agent-ui: `resets 1:40pm`), the `.limit` marker T-0260 writes also records it and the resume hint prints it, in both `run.sh` and `solo_run.py`.

## Context
Writers: plugins/sdlc-lite/scripts/run.sh (`<role>-<level>.limit`, hint `run.sh: session limit: resume with: <command>`) and plugins/sdlc-lite/scripts/solo_run.py (`<task dir>/solo.limit`, stderr hint). Add a `reset` JSON field (the text after `resets`, for example `1:40pm`; absent when the log has none) and append ` (resets 1:40pm)` to the hint. Existing selftests: run-selftest.sh case `session limit`, solo_run.py selftest. Another lane edits solo_run.py first (T-0293); build on top of it.

## Acceptance criteria
- [ ] `bash plugins/sdlc-lite/scripts/run-selftest.sh` case `session limit` has a variant whose log prints `resets 1:40pm`: the marker JSON has reset `1:40pm` and the stderr hint contains `resets 1:40pm`; the plain-failure and no-reset controls are unchanged.
- [ ] `python3 plugins/sdlc-lite/scripts/solo_run.py selftest` exits 0 with the same reset case for `solo.limit`.
- [ ] Negative control shown once for one writer: without the reset parse the new case fails.
- [ ] docs/references/sdlc-internals.md `run.sh` and `solo_run.py` session-limit sentences mention the reset time.

## Closed

2026-10-06: delivered by the solo agent (tier S); the ticket's own checks and the fanout gates passed
