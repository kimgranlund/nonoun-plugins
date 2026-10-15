---
id: T-0570
title: "Live Codex smoke run of one lane under the sibling worktree root"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: [T-0563, T-0564]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: claude 2026-10-15
branch: lane/T-0570-t0570
worktree: ../sdlc-lite.worktrees/T-0570-t0570
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---


## Goal
Evidence that one SDLC Lite lane runs end to end on Codex under the sibling worktree root: open, solo, verify, land, close. Every place Codex needs full access, or fails, is written down.

## Intent
- Do:
  1. In a throwaway git repo onboarded with the working-tree plugin, file one L1 ticket. Run its lane through Codex (`SDLC_BACKEND=codex`, the native subagent transport, per `docs/references/codex-role-execution.md`): `lanes.py open`, a solo role in the lane, a verifier, `fanout.py land`, then `tickets.py close` in main.
  2. Run it twice: once under `workspace-write`, and once with full access. Record which steps fail under the sandbox, and their errors.
  3. Write a dated report, `docs/reports/2026-10-<dd>-codex-live-lane.md`, holding the commands, codex-cli version, exit codes, and the path of each lane under `../<repo>.worktrees/`. Fix the Codex note in the `T-0564` guidance only where the run contradicts it.
- Non-goals: fixing Codex sandbox limits; Codex hook enforcement.
- Done when: the criteria pass.

## Context
The maintainer asked 2026-10-15 for one uniform ticket, worktree and branch system on Claude Code and Codex. T-0563 moves the root to `../<repo>.worktrees/`; T-0564 documents it, with the claim that lane operations need full access under Codex. The Codex live exchange is unverified (notes: T-0507, T-0316). codex-cli 0.162.1 is installed here.

## Constraints
Throwaway repo only. No push, no tag, nothing written to a consumer repo.

## Acceptance criteria
1. The report exists and lists each of open, solo, verify, land and close, with an exit code for each under both sandbox modes.
2. In the full-access run, the lane worktree path is under `<throwaway parent>/<name>.worktrees/` and the ticket ends `status: done` in main.
3. Any step that failed under full access is filed as its own ticket, with its id named in the report.
4. `git diff --check` exits 0.

## Outcome

2026-10-15 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full; verifier notes: note: the `redck.py deviations` run printed no `process deviation:` lines, and no `(red)` criterion exists in the handoff. | note: the four guidance edits use the same sentence, so the managed block in onboard.py (line 388) matches design.md:259. I did not run the onboard staleness tests, which no criterion names. | note: the ws verify and solo results rest on the launcher's own repair steps, and the report discloses them. I checked them against the logs only, since Codex must not be rerun.) · verifier: verifier-L2 (sonnet) · base: de7cf2031c18
- Changed: see commits
- Commits: 21ac238 T-0570: Live Codex smoke run of one lane under the sibling worktree root; dcbe7b8 T-0570: record lane
- Check: 1 Report lists open, solo, verify, land, close with an exit code per step under both sandbox modes: pass
- Check: 2 Full-access lane path is under `<throwaway parent>/<name>.worktrees/` and the ticket ends `status...: pass
- Check: 3 Each full-access failure is filed as its own ticket and named in the report: pass
- Check: 4 `git diff --check` exits 0: pass
