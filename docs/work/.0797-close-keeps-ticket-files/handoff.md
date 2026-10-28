---
id: T-0797
title: "tickets.py close deletes skips.md and other ticket-folder files (#83)"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-28
claimed_by: sdlc-lite-author 2026-10-28
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`tickets.py close` keeps every file in the ticket folder when it renames it to `.NNNN-<slug>` (GitHub #83).

## Repro
1. A ticket folder holds `handoff.md` and `skips.md`.
2. `tickets.py --root .sdlc close T-NNNN ...`.

## Expected
The closed folder `.NNNN-<slug>/` holds both files.

## Actual
Here: `git show --stat 5bc34f77` (close T-0790) and `git show --stat 23368535` (close T-0791) each delete a `skips.md`. ultimate-tokens-color-science restored it by hand in 6 commits (`git log --grep '#83'`, MacBook report row U1). Issue #83 is OPEN.

## Context
`plugins/sdlc-lite/scripts/tickets.py` close. Fleet retro 2026-10-28 row 13 (scored below 7 for an unmeasured cost; filed on the user's request).
outcome metric: `git log --grep '#83'` restore commits in ultimate-tokens-color-science after the release, before: 6.

## Acceptance criteria
1. A `tickets.py` selftest case: closing a ticket whose folder holds `skips.md` keeps it in the closed folder; with the fix reverted it fails (state the FAIL line).
2. tickets selftest through gate_lock exits 0, `check.py` exits 0.

## Constraints
The failing test lands before or with the fix, never after.

## Outcome
Fix: `tickets.py` `move_skips` unlinked a tracked `skips.md` at close, so a committed `skips.md` showed as deleted in the close commit. It now moves only an untracked `skips.md` to the records dir (T-0560 intent kept) and keeps a tracked one; the git-tracked check is shared with `move_records` as `tracked_names`. A committed deliverable such as `triage.md` already survived the rename (observed in the new case). The close gate is unchanged: `skips_path` reads the folder copy first, so `skip_missing` still finds it. The `close` docstring paragraph was updated.
Test first: the T-0560 selftest case became `(T-0797 plain|reason)`, now committing a `skips.md` and a `triage.md` and expecting the closed folder to keep both. Before the fix it failed with:
`FAIL (T-0797 plain) the closed folder keeps its committed files and moves an uncommitted skips.md: rc=0 '' ['.sdlc/.0001-tk/handoff.md', '.sdlc/.0001-tk/triage.md']` (and the same for `reason`).
Checks: `gate_lock.py run ... python3 plugins/sdlc-lite/scripts/tickets.py selftest` exit 0 (PASS), `python3 plugins/sdlc-lite/scripts/check.py` exit 0, `fanout.py selftest` PASS, `git diff --check` clean.
Open: an untracked, uncommitted `skips.md` still moves to the records dir by design (T-0560).

## Outcome

2026-10-28 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L2 (opus) · base: f11d3f72cf7c
- Changed: see commits
- Commits: 96f7a23 T-0797: tidy Outcome wording; b9b542b T-0797: close keeps a tracked skips.md in the ticket folder (#83)
- Check: 1 A `tickets.py` selftest case: closing a ticket whose folder holds `skips.md` keeps it in the clos...: pass
- Check: 2 tickets selftest through gate_lock exits 0, `check.py` exits 0: pass
- Follow-up: note: the conductor asked about the Goal -> notes.md
- Follow-up: decide: the untracked-moves branch is covered only by the selftest's no-git... -> notes.md
- Follow-up: fix-now: plugins/sdlc-lite/scripts/tickets.py:3604 close docstring still... -> notes.md
- Follow-up: note: docs/specs/sdlc-lite/design.md:5 "plus skips.md until a fanout... -> notes.md
- Follow-up: note: fanout.py selftest a close dependent was started under gate_lock... -> notes.md
