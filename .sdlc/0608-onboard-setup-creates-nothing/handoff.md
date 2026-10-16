---
id: T-0608
title: "onboard.py setup creates entry stubs and layout.md in a repo that never asked"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: claude 2026-10-15
branch: lane/T-0608-t0608
worktree: ../sdlc-lite.worktrees/T-0608-t0608
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`onboard.py setup` changes nothing a repo did not ask for. It refreshes an existing managed block in place. It appends a root block, creates `docs/` entry stubs, or writes `docs/layout.md` only with an explicit `--init` (or the equivalent flag the skill documents).

## Context
Reported by the gen-ui-kit conductor 2026-10-15 after `onboard.py setup` on 0.24.0 (reverted). gen-ui-kit is a bare clone with lanes at `<bare parent>/lanes/`, tickets in `docs/tickets` (`ticket_root:`), its own doc routing and AGENTS.md size gates, and an owner ruling that `.gitignore` stays as is. Check mode reported the root `AGENTS.md` as "unmanaged". Setup then appended a new block and created 24 `AGENTS.md` and `CLAUDE.md` files under `docs/` with a "Describe what this topic covers" placeholder and full file listings (`docs/tickets/AGENTS.md` listed every ticket), plus a new `docs/layout.md`. The 0.24.0 release note told every repo to rerun setup, which caused this.

## Intent
- Do: default setup refreshes existing managed blocks only and prints what `--init` would add. `--init` keeps today's behavior. Update `skills/onboard/SKILL.md` and the 0.24.0 upgrade notes (in the next release report) to say "refresh only".
- Non-goals: block content (the sibling ticket).
- Done when: the criteria pass.

## Constraints
A repo already set up keeps refreshing exactly as today.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/onboard.py selftest` exits 0. Its new cases cover:
   - a repo with no managed block and a `docs/` tree, where setup without `--init` changes no file and lists what `--init` would add;
   - the same repo with `--init`, which behaves as before.

   The cases failed before the change.
2. `git diff --check` exits 0.
