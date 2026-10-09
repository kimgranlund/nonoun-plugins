---
id: T-0398
title: "fanout replan lane reports verifier fail from a prior attempt's verifier result"
type: bug             # feature | bug | chore | spike | idea
status: done
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A fanout lane that is replanned after a failed first attempt reads only the verifier result of its own latest attempt, so a stale `verifier-L2.md` from attempt 1 no longer produces `verifier fail`.

## Intent
- Do: in scripts/fanout.py find where a lane's verifier outcome is read after the lane's task folder is merged or reused (T-0381 attempt 2 showed it: the new `verifier-L3.md` said pass, 6 pass 0 fail, while the merged-in `verifier-L2.md` from attempt 1 said fail and the lane reported `verifier fail`). Pick the result with `order.py` newest-result ordering (never mtime), or scope the read to the current attempt id.
- Non-goals: model or effort changes; deleting prior attempts' results.
- Done when:
  - A fanout selftest case, observed failing first: a lane folder holding an older failing verifier result and a newer passing one reports pass.
  - fanout.py selftest, check.py and tickets.py check pass.

## Context
Seen 2026-10-08 on the T-0381 second attempt (commit 57c423a6 "wip(T-0381): verifier fail").

## Constraints
No em or en dashes. No push or publish.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0 and `grep -c 'case 15 verdict T-0398' plugins/sdlc-lite/scripts/fanout.py | grep -qx 3` exits 0 (the selftest prints only misses, so exit 0 means the three T-0398 cases held: an older recorded fail with a newer unrecorded pass reads pass; the baseline still excludes a stale file; with both recorded the later record wins).
- `git diff` of `plugins/sdlc-lite/scripts/fanout.py` shows `solo_verdict` and `branch_verdict` both reading through `newest_verifier`, and no file mtime read.
- `python3 plugins/sdlc-lite/scripts/check.py` and `python3 plugins/sdlc-lite/scripts/tickets.py check` exit 0.

## Closed

2026-10-09: delivered by the solo agent (level L2); verified pass by an L2 verifier on the second attempt after one criterion swap
