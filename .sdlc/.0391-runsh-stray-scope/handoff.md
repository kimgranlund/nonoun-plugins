---
id: T-0391
title: "run.sh reports only the role's own stray worktrees and branches, like dispatch.py record"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0381]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`run.sh` reports a stray worktree or branch only when it belongs to the role's own run, so sibling lanes the parent creates during a native exchange no longer produce warnings.

## Intent
- Do: scripts/run.sh has its own stray reporter (`report_strays`, about lines 538 to 550, called after a native exchange) that diffs the whole repo's worktree and branch lists. T-0371 (0.22.0) scoped only `dispatch.py record`. Apply the same scope in run.sh: compare against the role's own tmp prefix and branch prefix, and share the matching rule with dispatch.py instead of copying it (a small helper both call, or one documented rule). Keep reporting the role's own strays, and keep the exit code unchanged.
- Non-goals: model or effort changes; changing what counts as a stray for the role itself.
- Done when:
  - A run-selftest case (observed failing first): a sibling lane worktree and branch created by the parent during an active native exchange are not reported; a stray created by the role itself still is.
  - check.py, tickets.py check, run-selftest.sh, dispatch selftest, both generate --check pass.

## Context
Maison and Codex, 2026-10-08: sibling stray warnings recurred on the 0.22.0 runner, not a stale profile. Codex recorded the exact warning blocks, the executed run.sh path and its sha256 8a7e7123e3996de9cb03c80c57032ca15fea48948ad00c8f86eb86652fcf219f in maison .sdlc/tickets/0285-codex-role-preflight/live-profile-version-gap-2026-10-08.md; the runner emitted them at lines 544 and 547 after a native exchange while the parent created T-0303 and T-0294 sibling lanes during active runs. T-0371 was verified only for dispatch.py record, so this is the run.sh half. Starts after T-0381, which edits run.sh.

## Constraints
No em or en dashes. No push or publish.

## Closed

2026-10-08: delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed
