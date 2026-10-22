---
id: T-0705
title: "dispatch.py status prints one unrecorded-report flag"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P3         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-21
claimed_by: sdlc-lite-author 2026-10-21
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`dispatch.py status` names an unrecorded report with one token, not two.

## Intent
- Do: merge `report-written-unrecorded` (T-0383) and `report-unrecorded` (T-0703) in `plugins/sdlc-lite/scripts/dispatch.py` into one token that fires for every state the two cover today; update every reader and doc that names either token.
- Non-goals: changing which states are flagged.
- Done when: the criteria pass.

## Context
T-0703 verifier: "Running or orphaned with a newer report prints both tokens. Running or orphaned with an older report ... prints only the old one. Only the new token covers interrupted and limit-stopped."

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0, and its cases show a running attempt with a newer report prints exactly one flag token.
2. `git grep -n "report-written-unrecorded\|report-unrecorded" plugins docs/references` shows only the kept token.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0 and `git diff --check <base sha>` exits 0.

## Outcome
Kept `report-unrecorded`: the conductor agent, its generated Codex definition, and the T-0703 docs name it, and it is the only token that also covers interrupted and limit-stopped attempts. `dispatch.py status` now adds it once when a report file exists and the attempt is running or orphaned (T-0383 shape), or is any state but completed or failed with a report newer than its record (T-0703 shape); no flagged state changed. `report-written-unrecorded` is gone from `dispatch.py` and `docs/references/sdlc-internals.md`. Selftest: the old T-0703 control "older report is not flagged" now uses an interrupted attempt (a running one with an older report was always flagged by the T-0383 token), plus new cases for a running attempt with an older and a newer report printing exactly one token.

Checks: `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exit 0, `git grep -n "report-written-unrecorded\|report-unrecorded" plugins docs/references` shows only `report-unrecorded`, `python3 plugins/sdlc-lite/scripts/check.py` ok, `python3 scripts/check-packaging.py` PASS, `git diff --check 12785ab2` exit 0.

## Outcome

2026-10-21 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L2 (opus) · base: 12785ab2d7d8
- Changed: see commits
- Commits: 7866970 T-0705: dispatch.py status prints one report-unrecorded flag
- Check: 1 `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0, and its cases show a running at...: pass
- Check: 2 `git grep -n "report-written-unrecorded\|report-unrecorded" plugins docs/references` shows only t...: pass
- Check: 3 `python3 plugins/sdlc-lite/scripts/check.py` exits 0 and `git diff --check <base sha>` exits 0: pass
- Follow-up: note: docs/references/sdlc-internals.md:29 the added clause "so a running... -> notes.md
