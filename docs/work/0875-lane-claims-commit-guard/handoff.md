---
id: T-0875
title: "A lane cannot land or mark ready a change to a path another lane owns, and a user can wire the same check as a"
type: feature        # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0874]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-19
claimed_by: nonoun-author 2026-11-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A lane cannot land or mark ready a change to a path another lane owns, and a user can wire the same check as a git pre-commit hook.

## Intent
- Do: add `lanes.py claims check [--staged]` and run it from `ready` and `finish`.
- Non-goals: installing a git hook automatically; enforcing on Codex beyond what the scripts do.
- Done when: the criteria below hold.

## Context
- #102 asks for "a pre-commit check in a lane worktree [that] refuses a commit that adds or changes a path claimed by another lane, and names the owner", with append-marked paths warned, not refused.
- Uses the claims store from lane-path-claims. `ready` (`lanes.py:2072`) and the `finish` commit steps (ticketed and `finish_ticketless`) are the plugin's own commit points; a git pre-commit hook in `.git/hooks` is shared by every worktree of the repo, so installing one is the user's choice. Show the one-line hook in the docs instead.
- `claims check`: in the current lane tree, the changed paths (staged with `--staged`, else `lane_paths`) that match a glob owned by another open lane exit 1 with `owned by <lane>: <path> (<glob>)`; append-marked matches print `append: <path> also claimed by <lane>` and exit 0. Outside a lane it exits 0 with `not in a lane`.
- Run scripts with `export SDLC_ALLOW_STALE_PLUGIN=1`. Read `plugins/sdlc/AGENTS.md` first.

## Do
1. Add `claims check`.
2. Call it from `ready` and both `finish` commit steps; a refusal stops with nothing pinned, committed or merged.
3. Add selftest cases (owned path refused at ready and finish, append path warned, own claim passes) and document it with the pre-commit hook line in the docstring and the CHANGELOG `[Unreleased]`.

## Acceptance criteria
- The lanes selftest shard holding the new cases exits 0; with the call removed from `ready`, the ready case fails (state the observed red).
- `bash plugins/sdlc/scripts/check.sh --fast` exits 0 and `git diff --check` is clean.

## Constraints
- No file under `.git/hooks` is written by any command.
