---
id: T-0570
title: "Live Codex smoke run of one lane under the sibling worktree root"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: [T-0563, T-0564]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
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
