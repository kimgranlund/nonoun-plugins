---
id: T-0685
title: "record --agent-id ignores short heading-less stdin when the transcript holds a complete result"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
claimed_by: sdlc-lite-author 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`dispatch.py record --agent-id` keeps a passing role passing when the caller fed a short placeholder on stdin (such as `echo x |`): it ignores that stdin with a warning and takes the transcript's complete result, while real error text on stdin still fails the attempt.

## Intent
- Do: in `record` (`plugins/sdlc-lite/scripts/dispatch.py`, the stdin branch near line 1700), when the transcript's final message is complete (not `max_tokens`) and holds a `## ` heading, and stdin is one line under 40 characters with no heading that matches neither `LIMIT_RE` (near line 1343) nor an error word (error, terminated, fail, abort, killed, exception, timeout), ignore stdin, print `dispatch.py: ignored stdin "<text>" (no heading, under 40 chars); recorded the transcript's final message`, and record the transcript result.
- Do: update the record paragraph near line 131 (`any other stdin is the sub-agent's error text`) and the `record` docstring near line 1657 to name the exception.
- Do: add a selftest case beside the T-0349 table near line 3584: `record --agent-id` with stdin `x` and a complete transcript exits 0 and its stderr has `ignored stdin`. The existing `t2` (`Error: session limit reached`) and `r6` (`Agent terminated unexpectedly`) cases stay failures.
- Non-goals: changing behavior when stdin has a heading, or when no transcript is found.
- Done when: the criteria pass.

## Context
Source: GitHub issue #36, ui-kit 0.27 vs 0.28 measurement 2026-10-21.
`echo x | dispatch.py record .../verifier-L2.dispatch.json --agent-id a0157-...` printed `verifier returned no result` and closed the attempt `failed`; the conductor re-dispatched 0157-verifier-L2-2. On main 8624f984 the rule sits at `dispatch.py:1704` (`is_err = bool(said.strip()) and not has_head and not (fin and ...)`), and the selftest `record r6: unmatched error stdin is a failure despite a complete transcript` (near line 3606) pins it. The issue's "under 40 chars" rule alone is partly false: `r6` sends `Agent terminated unexpectedly` (29 chars) with a complete transcript and must stay a failure, so the error-word test is required.

## Constraints
The T-0646 pointer-with-no-file case and the T-0412 empty-stdin case keep their behavior.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0 with the new case, and the new case fails with the change reverted.
2. The existing `record t2` and `record r6` cases still pass.
3. `git diff --check <base sha>` exits 0.

## Outcome
`record` (`plugins/sdlc-lite/scripts/dispatch.py`) now ignores a one-line stdin under 40 characters with no heading, no `LIMIT_RE` match and no error word when the transcript's final message is complete and holds a `## ` heading: it prints `dispatch.py: ignored stdin "<text>" (no heading, under 40 chars); recorded the transcript's final message` and records the transcript. Module doc and `record` docstring name the exception. New selftest case `record --agent-id with placeholder stdin x ...` beside the T-0667 cases; it fails with the code change reverted (observed) and passes with it. `dispatch.py selftest` exit 0 (t2, r6 still pass); `check.py` exit 0; `git diff --check a3147a26` exit 0.
