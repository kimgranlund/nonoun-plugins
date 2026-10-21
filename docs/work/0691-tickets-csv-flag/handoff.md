---
id: T-0691
title: "accept --tickets T-1,T-2 on lanes.py open, fanout.py land and tickets.py claim"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P3         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A conductor can pass several tickets as one comma-separated argument, so a zsh string or loop no longer breaks multi-ticket calls, and the conductor guidance says to wrap shell loops in `bash -c`.

## Intent
- Do: add `--tickets T-1,T-2` to `lanes.py open` (`plugins/sdlc-lite/scripts/lanes.py`, the open parser near line 1886, merged into `--ticket` in order, duplicates dropped) and to `tickets.py claim` (`plugins/sdlc-lite/scripts/tickets.py`, parser near line 8947, claiming each id in turn and exiting non-zero if any claim fails). Update the `lanes.py` docstring usage line 4 and add a `--tickets` row to `## Arguments` in `plugins/sdlc-lite/skills/ticket/SKILL.md`.
- Do: one sentence in `plugins/sdlc-lite/agents/conductor.md` (`## Merge ops` or `## Stay thin`): Bash runs zsh on the Claude host, so a loop or a flag list built in a string goes inside `bash -c '...'`.
- Do: a selftest case in each script: `--tickets T-1,T-2` gives the same result as two `--ticket` (or two claim calls).
- Non-goals: `fanout.py land --tickets`: land takes one branch and one ticket per call (`cmd_land`, fanout.py:2494, `--ticket` at line 5744 is single by design), so the `expected one argument` evidence is the zsh word-splitting failure the `bash -c` sentence covers.
- Done when: the criteria pass.

## Context
Source: GitHub issue #43, ui-kit 0.27 vs 0.28 measurement 2026-10-21.
- `lanes.py: error: unrecognized arguments:  --ticket T-0130 --ticket T-0129 ...` for 6 lanes: a flag string passed as one argument.
- `fanout.py land: error: argument --ticket: expected one argument`, twice; one conductor needed reruns under bash twice.
- 14 conductor and 268 role results show zsh `no matches found` (regex count, unverified).
- On main `lanes.py open` has `--ticket` with `action='append'` (lanes.py:1886) and `tickets.py claim` takes one positional `id` (tickets.py:8949).

## Constraints
`--ticket` keeps working unchanged; mixing `--ticket` and `--tickets` concatenates.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/lanes.py selftest` and `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exit 0 with the new cases, and each case fails with its flag removed.
2. `git grep -n -- "--tickets" plugins/sdlc-lite/skills/ticket/SKILL.md` shows the Arguments row, and `git grep -n "bash -c" plugins/sdlc-lite/agents/conductor.md` shows the sentence.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
4. `git diff --check <base sha>` exits 0.
