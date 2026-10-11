---
id: T-0424
title: "Add the git-native conventions to the lane lifecycle design: names, archive refs, worktree lock, worktree config"
type: feature        # feature | bug | chore | spike | idea
status: proposed
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0422]
created: 2026-10-10
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The lane lifecycle design (docs/specs/sdlc-lite/lane-lifecycle.md, T-0422) carries the git-native conventions the maintainer approved, with the build tickets they imply.

## Intent
- Do: after T-0422 lands, extend docs/specs/sdlc-lite/lane-lifecycle.md (design only, Markdown). Add and decide: (1) branch namespaces `lane/<ticket>-<slug>`, `wave/<N>`, `release/<X.Y.Z>`, the directory/branch-clash rule (`lane` vs `lane/x`), and the migration (old names keep working; sweep reads both); (2) `refs/archive/<date>/<branch>` replacing the text log, and how a branch is recreated; (3) `git worktree lock --reason` set at lane open and cleared at close, sweep and prep skipping locked lanes, and the finished-agent lock that must be cleared; (4) `extensions.worktreeConfig` with `git config --worktree lane.port <n>` replacing `.lane.json`, with the consumer setup cost and a fallback when the extension is off; (5) `branch.<name>.description` carrying `<ticket> <title>`; (6) fold sweep.py into the plugin as one authoritative script and say how fanout land, tickets close and dispatch prune call it; (7) the checks (no lane worktree under a checkout, stale lane report) with a negative control each; (8) build tickets with sizes.
- Non-goals: writing scripts; deleting branches or worktrees.
- Done when:
  - The design names every file a build changes, each new check with a negative control, and the ordered build tickets; docs_check.py and check.py pass; no dashes.

## Context
gen-ui-kit, 2026-10-10: `lane-wait`'s `gh pr merge --auto` is tested; it needs `--squash` (or `--merge`, `--rebase`) and merged PR 425 on green. Merges were approved by the owner per PR, so keep the opt-in per PR, never default or blanket. The design records this instead of listing the merge call as untested.
Maintainer decision 2026-10-10: adopt all of the git-native conventions including worktree config. Depends on T-0422, whose design lane is running; its handoff stays frozen, so this is the addendum.

## Constraints
No em or en dashes. No push or publish. Do not remove any worktree or branch.
