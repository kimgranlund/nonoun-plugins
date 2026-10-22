---
id: T-0739
title: "A stale open copy that matches a committed version is dropped"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-22
claimed_by: sdlc-lite-author 2026-10-22
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`drop_stale_open` (T-0723, T-0738) treats an open `NNNN-*` copy as stale, and drops it, when every file in it matches a version of the same ticket folder already committed on the target branch's history (for example the pre-replan handoff re-added from main); it still refuses when the open copy holds content no committed version had.

## Intent
- Do: in `plugins/sdlc-lite/scripts/fanout.py` (`open_adds`, about line 1683), before flagging a file, check whether its blob equals any blob that path (open or closed folder name) had in the target's history (`git log --format= --raw` or `git rev-list` over the path); count such a file as not added. Add a selftest case: a ticket whose handoff was replanned inside its lane, closed on integration, then its pre-replan open copy re-added from main is dropped; the T-0738 extra-file and edited-body cases still refuse.
- Non-goals: merging edits.
- Done when: the criteria pass.

## Context
T-0738 verifier-L2 (landed):
- note: plugins/sdlc-lite/scripts/fanout.py:1683 a normal close (front matter rewrite plus an appended `## Outcome`, then the rename) is not flagged: case 23 (T-0723) runs a real land and close and still drops the copy. A probe over this repo's own history found 297 versions of open handoffs from first-parent main. For 287 of them, the body is a prefix of the closed body.

## Acceptance criteria
1. The new `fanout.py` selftest case passes, the T-0723 and T-0738 cases still pass, and with the history check removed the new case fails (state the FAIL line).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
`open_adds` in `plugins/sdlc-lite/scripts/fanout.py` now collects the (path, blob) pairs both folder names held in HEAD's history (`git log --raw --no-abbrev`) and counts a file whose index blob is among them as not added. New selftest case 23 variant `-replan` (lane replans the handoff, closes, pre-replan open copy re-added from main) is dropped; the `-extra` and `-edit` cases still refuse.
- Negative control: with the history check neutralised (`not in set()`), the selftest prints `FAIL ... case 23 stale open folder (T-0739): the pre-replan open copy of a ticket replanned in its lane ... got rc2=0 rc=1`, exit 1.
- `gate_lock.py run ... fanout.py selftest` exit 0, `check.py` exit 0, `check-packaging.py` exit 0, `git diff --check 963a8bd8` exit 0.

## Outcome

2026-10-22 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L2 (opus) · base: 963a8bd8eb6f
- Changed: see commits
- Commits: 6f4c760 T-0739: a stale open copy that matches a committed version is dropped
- Check: 1 The new `fanout.py` selftest case passes, the T-0723 and T-0738 cases still pass, and with the hi...: pass
- Check: 2 `gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/fanout.py se...: pass
- Follow-up: note: plugins/sdlc-lite/scripts/fanout.py:1682 replay of the T-0738 finding -> notes.md
- Follow-up: note: plugins/sdlc-lite/scripts/fanout.py:1683 the cost is bounded -> notes.md
- Follow-up: decide: plugins/sdlc-lite/scripts/fanout.py:1683 the log uses default... -> notes.md
