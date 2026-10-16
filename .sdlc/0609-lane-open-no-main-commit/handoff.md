---
id: T-0609
title: "lanes.py open commits its record onto local main, which diverges from origin in PR repos"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: claude 2026-10-15
branch: lane/T-0609-t0609
worktree: ../sdlc-lite.worktrees/T-0609-t0609
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`lanes.py open` never leaves a commit on the default branch that the repo's landing path does not push. In a repo that lands through PRs (squash merges on origin), local main stays fast-forwardable to origin after any number of lane opens.

## Context
Reported by the agent-ui conductor on 2026-10-15, against 0.24.0. Since T-0599, `lanes.py open` commits "T-NNNN: record lane <lane>" on the main checkout. The commit edits only `.sdlc/AGENTS.md` and `.sdlc/roadmap.md`. agent-ui lands by PR squash merge and never pushes those commits, which caused three problems:
- local main diverged from origin, so `git pull --ff-only` in its post-merge sync failed;
- a store PR cut from local main came out CONFLICTING;
- a merge sync restored tracked open copies of locally closed tickets, and the next close refused with "duplicate id".

Its workaround is to reset main to origin after each lane open. T-0588 already makes the claim a git ref (`refs/sdlc/claims/<id>`), so the claim no longer depends on a commit on main. In this repo (local land into main, no PR), the T-0599 behaviour works and must keep working: `lanes.py finish` must not hit a dirty main.

## Intent
- Do: choose where the open record goes so neither repo kind breaks. Candidates: commit it on the lane branch, so it merges back with the lane; or commit on main only when the lane lands locally into main (no upstream ahead, or no PR land mode).
- Do: document the chosen behaviour in the lanes section of the plugin AGENTS.md and in `docs/references/sdlc-internals.md`.
- Non-goals: changing how claims or ids are reserved.
- Done when: the criteria pass.

## Constraints
- The main checkout's tracked files stay clean after `lanes.py open`, as T-0599 required.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/lanes.py selftest` exits 0, with two new cases:
   - A fixture main that tracks an upstream (a PR-style repo): after `lanes.py open`, `git rev-list origin/main..main` is empty, and `git status --porcelain` in the main checkout is empty.
   - The existing local-land fixture: `lanes.py finish` still lands and closes.

   The first case failed before the change.
2. `git diff --check` exits 0.
