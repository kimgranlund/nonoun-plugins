---
id: T-0600
title: "Codex docs name the ticket folder for solo request files; they land in the records dir"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: claude 2026-10-15
branch: lane/T-0600-t0600
worktree: ../sdlc-lite.worktrees/T-0600-t0600
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The Codex docs name the directory where a native solo or verifier request file appears, as the live run found it.

## Intent
- Do:
  1. In `docs/references/codex-role-execution.md` and `plugins/sdlc-lite/adapters/codex/instructions.md`, replace `<ticket folder>/solo-<level>-<attempt>.request.json` and "beside the handoff" with the records dir that `order.py records-dir <ticket folder>` prints (`.sdlc/runtime/tasks/<slug>/` in the T-0570 run).
  2. Regenerate the Codex agents if `instructions.md` feeds them, and run their freshness check.
- Non-goals: moving the request file.
- Done when: the criteria pass.

## Context
The T-0570 live run (codex-cli 0.162.1, report `docs/reports/2026-10-15-codex-live-lane.md`) found `solo-L1-<attempt>.request.json` and `verifier-L1.request.json` under `<lane>/.sdlc/runtime/tasks/greeting/`, not in `<lane>/.sdlc/greeting/`. The Codex conductor's glob on the documented path failed (`zsh:1: no matches found: .sdlc/greeting/solo-L1-*.request.json`) and it found the file by search.

## Constraints
None.

## Acceptance criteria
1. `git grep -n "ticket folder>/solo-" -- docs plugins` prints nothing.

## Outcome

2026-10-15 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full; verifier notes: note: `plugins/sdlc-lite/scripts/solo_run.py:44` still says `--request-file <task dir>/solo-<level>-<attempt>.request.json`. This is stale against `:252`, but it is a script docstring outside the criterion and the `docs plugins` grep pattern. | note: `docs/references/codex-role-execution.md:89` and `plugins/sdlc-lite/adapters/codex/instructions.md` now describe the `run.sh` request path (`<role>-<level>[-k].request.json`) as "in the handoff's records dir". That matches `run.sh:250` and `:486`. The verifier request file is covered by this role-step text rather than a separate line.) · verifier: verifier-L2 (sonnet) · base: 75fdb679a2ab
- Changed: see commits
- Commits: 35583c7 T-0600: Codex docs name the ticket folder for solo request files; they land in the records dir
- Check: 1 `git grep -n "ticket folder>/solo-" -- docs plugins` prints nothing: pass
