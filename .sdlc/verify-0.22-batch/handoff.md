# Verify T-0361, T-0362, T-0364, T-0365, T-0366 on main

## Goal
Independently verify five closed solo tickets on main at HEAD (builders were solo sonnet; you are a different family). T-0361 and T-0362 finish the Claude headless retirement (the earlier verifier passes are in .sdlc/verify-retire-solo-gate/verifier-L3.md, which found the two leftovers T-0362 fixes). T-0364, T-0365, T-0366 come from the 2026-10-08 fleet retro.

## Intent
- Do: for each ticket read its closed folder (.sdlc/.NNNN-*/handoff.md) and check each Done-when criterion with an observed command in a throwaway git archive copy of HEAD (git-initialised, under your tmp prefix; no worktrees), with a red control where a criterion is a guard. For T-0362 specifically re-run the earlier verifier's observations: fanout.default_driver('h.md','solo','L1'|'L2') refuses without SDLC_CLAUDE_EXEC=1 and returns the command with it; a two-lane fanout.py run without the flag reports the pointer in the report row for both lanes and starts no stub claude; the three stale text lines are repaired.
- Non-goals: editing anything.
- Done when: a pass or fail per ticket with the command and output per criterion.

## Context
T-0361 Done-when (.sdlc/.0361-retire-solo-gate/handoff.md):
  - `solo_run.py run --exec` with the flag unset on the Claude backend exits 2 with the one-line pointer, with the flag set it starts as before (selftests cover both); the fanout lane path (`fanout.py prep`/`land`, `--driver CMD`) is unaffected.
  - Deleting the default_driver gate makes check.py fail (observed), restored it passes.
  - `grep -rn "legacy default\|until T-0288" plugins docs/references` finds no stale statement (dated reports stay history).
  - check.py, tickets.py check, both generate --check, run-selftest.sh, solo_run, fanout and dispatch selftests, and check.sh pass.

T-0362 Done-when (.sdlc/.0362-retire-leftovers/handoff.md):
  - The new selftest case fails on the pre-change fanout.py (observed) and passes after; a two-lane `fanout.py run` without the flag (stub claude on PATH, one L1 and one L3 ticket) shows the pointer in the report row for both lanes and starts no stub.
  - `grep -n "T-0288" docs/references/sdlc-internals.md plugins/sdlc-lite/scripts/fanout.py plugins/sdlc-lite/skills/fanout/SKILL.md` shows no statement that a retirement is still to come.
  - check.py (the _fn_body guard still holds), tickets.py check, both generate --check, fanout, solo_run and dispatch selftests, and check.sh pass.

T-0364 Done-when (.sdlc/.0364-replan-loop-small-gaps/handoff.md):
  - A selftest: a review with only Notes-level findings passes with Notes appended; one with a real defect still replans (observed failing first).
  - check.py, tickets.py check, the affected selftests and both generate --check pass.

T-0365 Done-when (.sdlc/.0365-widen-allowlist/handoff.md):
  - A selftest: widen with an explicit file list succeeds and records the reason; widen with neither the list nor the criterion still refuses (observed failing first).
  - check.py, tickets.py check, the affected selftests and both generate --check pass.

T-0366 Done-when (.sdlc/.0366-prepare-base-sha/handoff.md):
  - A selftest: a solo dispatch with a recorded base sha and a later commit makes prepare verifier print the recorded sha (observed failing first, printing HEAD).
  - check.py, tickets.py check, the affected selftests and both generate --check pass.

## Constraints
Read-only. No em or en dashes.
