---
id: T-0537
title: "dispatch.py: a sub-agent stopped by the spend limit is resumable, and prepare notes a changed model or effort (maison T-0546)"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-13
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
dispatch.py: a sub-agent stopped by the spend limit is resumable, and prepare notes a changed model or effort.

## Intent
- Do: a sub-agent that ends with a spend or session limit and no `record` leaves the attempt `running`; `status` and `resume` then say nothing useful. Give the conductor a route: `dispatch.py resume <name> --limit` (or `record --limit`) marks the attempt limit-stopped, writes the `.limit` file with the resume command, and the conductor text in `agents/conductor.md` says a `SendMessage` to the agent by name resumes it with its context.
- Do: `prepare` prints one line when the role level's model or effort differs from the previous attempt recorded for the same ticket in `runs.jsonl`.
- Non-goals: detecting the limit automatically from the host.
- Done when: `dispatch.py selftest` and `lifecycle-selftest.py` pass with the limit route (positive, and a refusal for an attempt that has a result, negative control) and the changed-row notice (printed on a change, silent on none). The same was seen here on 2026-10-13 (wave 64, T-0531).

## Context
maison T-0546 observations 37, 38: `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/0546-sdlc-lite-work-record-improvements/observations.md` (section "Added after the author's reply"). Read only; never edit maison.

## Constraints
A new or changed check needs a positive case and an observed negative control.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0; its T-0537 cases cover `resume --limit` on a running attempt with no result (status limit-stopped, .limit marker holding the SendMessage-by-name call and the prepare command, record still works after the resume), a refusal for an attempt that has a result and for a completed one (negative controls), and the prepare row-changed line printed on a changed model or effort and absent on a matching row.
- `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py` exits 0.
- `bash plugins/sdlc-lite/scripts/check.sh` exits 0 (generated Codex conductor TOML fresh).
- `plugins/sdlc-lite/agents/conductor.md` tells the conductor to run `dispatch.py resume --limit <name>` and to resume the agent with a `SendMessage` by name.

## Closed

2026-10-13: solo L2 built, verifier L2 pass with observed negative controls (rerun after limit stop), merged from fanout/wave66-k
