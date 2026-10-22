---
id: T-0710
title: "Fix four verifier-flagged doc and test gaps"
type: chore           # feature | bug | chore | spike | idea
status: ready        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-21
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Four verifier notes from tonight's waves are fixed: one vacuous selftest case and three stale doc lines.

## Intent
- Do:
  1. `plugins/sdlc-lite/scripts/gate_lock.py` (about line 1466): make the case_rr "over the load cap with a grant held" check refuse because of the load cap, not capacity (for example entries that fit capacity), so it fails if the cap check is removed.
  2. `docs/specs/sdlc-lite/gate-lock-admission.md` (about line 213): the Reason bullet says `status --json` `over` is true only while a grant or legacy holder is held (gate_lock.py about line 795).
  3. `docs/references/sdlc-internals.md` (about line 29): fix the unbalanced parenthesis.
  4. `plugins/sdlc-lite/skills/fanout/references/land.md` (about line 15): the warning fires for each `--gate` and `--light-gate` (fanout.py about line 2240).
- Non-goals: behavior changes.
- Done when: the criteria pass.

## Context
Verifier notes copied from `docs/work/NOTES.md`:
- note: plugins/sdlc-lite/scripts/gate_lock.py:1466 the case_rr "over the load cap with a grant held" check is vacuous against cap removal: every entry needs 6 compute units and the held grant uses 1, so capacity alone refuses them (mutant D left case_rr GREEN). Likewise "then the cap holds" after b3 is held by capacity, not the cap. The real-process case_load_idle carries this proof instead.
- note: docs/specs/sdlc-lite/gate-lock-admission.md:213 the Reason bullet does not say `status --json` `over` is now true only while a grant or legacy holder is held (gate_lock.py:795).
- note: docs/references/sdlc-internals.md:29 the added clause "so a running attempt with a report prints it once)" closes a parenthesis that has no opening one in that sentence.
- note: plugins/sdlc-lite/skills/fanout/references/land.md:15 says the warning fires "for each `--gate`", but the code (fanout.py:2240) also checks `--light-gate`. The fanout.py docstring at line 43 names both.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/gate_lock.py selftest` exits 0, and with the load-cap check in gate_lock.py disabled in a scratch copy the fixed case fails (state the observed FAIL line in the Outcome).
2. `git diff <base sha> -- docs/specs/sdlc-lite/gate-lock-admission.md docs/references/sdlc-internals.md plugins/sdlc-lite/skills/fanout/references/land.md` shows each of items 2 to 4.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0, `python3 scripts/check-packaging.py` passes, and `git diff --check <base sha>` exits 0.
