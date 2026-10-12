---
id: T-0483
title: "/report lanes and /report waves views: lane and wave status with tickets and percent"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`/sdlc-lite:report lanes` and `/sdlc-lite:report waves` print the fanout and solo lane state of the repo, so the maintainer reads the answer to "which waves remain, with which tickets, at what percent" in one command instead of piecing it from `git branch`, `ps` and the board.

## Intent
- Do: add two views to `plugins/sdlc-lite/scripts/report.py` and `skills/report/references/views.md` (and the Views table in the skill if it lists them). `lanes`: one row per lane worktree or lane branch from `lanes.py` (lane, ticket, stage, driver alive, commits ahead of main, landed or not, lane directory). `waves`: group lanes by integration branch (`fanout/waveNN`, `fanout/<date>`); per wave list its tickets, each ticket's stage and percent, the integration branch's commits ahead of main, whether the wave is merged into main, and a wave percent. Percent comes from one derivation: the ticket's step verdicts via `steps.py`/`progress.py` ladder (builder 10, reviewer 70, verifier 90, closed 100); a ticket with no plan shows its stage word. Both views read records only, make no model call, and mark a field they cannot read `unknown`.
- Non-goals: any write or cleanup (lane removal stays `lanes.py`/the sweep); cross-session reads (`--session` stays reserved); changing the `summary` view; a new table format beyond the existing views.
- Done when: `python3 plugins/sdlc-lite/scripts/report.py selftest` covers both views against a fixture with two waves (one running, one merged and closed) and an observed-red case for each (today the view is refused as unknown); `report lanes` and `report waves` run on this repo and agree with `git branch --list 'fanout/*'`; `check.py` and `check.sh` exit 0.

## Context
Origin: maintainer request 2026-10-12 after the wave 40 and 41 status check. That check needed `git rev-list main..fanout/waveNN`, `fanout.log` tails and `pgrep`; the generic RAG board listed 30 old plans and missed that both waves had finished. The report skill shipped in T-0460 (`skills/report/`, `scripts/report.py`, `references/views.md`); lane data lives in `scripts/lanes.py` (T-0451) and `fanout.py` land journals (`<lanes-dir>/logs/land.jsonl`, `fanout.log`). Wave 41 lanes live under `.worktrees/fanout41`, so the view must read each `--lanes-dir` from the land journal or git worktree list, not assume `.worktrees/fanout`.

## Constraints
No model call. Views stay within the report skill's line budget rules. State only what a command shows. Prompt wording follows the controlled language set; no new prohibitions.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/report.py selftest` exits 0 and prints the cases `lanes`, `waves`, the two `control ... view: red without the rule, green with it` lines, and the `refused as unknown (observed red)` line.
- `python3 plugins/sdlc-lite/scripts/report.py render lanes --no-snapshot` and `render waves --no-snapshot` exit 0 on this repo; the branches in the lanes view equal `git worktree list` branches under `fanout/`.
- `python3 plugins/sdlc-lite/scripts/check.py` exits 0 and `bash plugins/sdlc-lite/scripts/check.sh` exits 0.
- `skills/report/references/views.md` lists the `lanes` and `waves` views.

## Closed

2026-10-12: delivered by the solo agent (level L2); one independent batched verifier passed before the merge
