---
id: T-0422
title: "lane-open, lane-close and lane-wait: design and build plan from the gen-ui-kit spec"
type: feature        # feature | bug | chore | spike | idea
status: ready
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-10
claimed_by: claude 2026-10-10
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A written design and build plan so a lane is opened, tracked and closed by the plugin, and finished lanes no longer pile up as worktrees, branches and gigabytes.

## Intent
- Do: design only, Markdown, docs/specs/sdlc-lite/lane-lifecycle.md with a status line. Read source/SPEC.md and source/*.sh in this folder (from the gen-ui-kit conductor, tested there), scripts/fanout.py (prep, land, the .worktrees layout), scripts/dispatch.py (prune), scripts/tickets.py (close), hooks/block-stray-worktree.sh, docs/references/claude-hooks.md and AGENTS.md invariants (preserve unrelated worktrees, branches and stashes). Decide and write down: (1) where lane worktrees live, since the spec puts them outside every checkout while fanout and the stray-worktree hook use .worktrees and .claude/worktrees today, and what changes in the hook, the ignore rules and the watcher exclusions; (2) lane-open / lane-close / lane-wait as plugin scripts or skills versus fanout.py subcommands, one authoritative home, no copied tables; (3) the squash-merge test (every changed file equals origin/main) and its negative control; (4) port assignment from .lane.json and its relation to gate_lock; (5) how fanout land, tickets close and dispatch prune call close, and a `lane still open` line; (6) the checks the spec lists (no lane under a checkout, stale lane report) with a negative control each; (7) consumer repos: what a conductor must change, what stays optional; (8) the known gaps in the spec (untested `gh pr merge --auto`, hard-coded Node path, branch-name equals remote-ref crash) as explicit risks, with an authorization note: auto-merge acts under the owner account, so it needs a written opt-in and is never default; (9) the build split into tickets with sizes and a live-run plan on a throwaway repo; (10) a cleanup plan for the existing pile (this repo has 144 worktrees, 252 branches and 4.4 GB under .worktrees) that is a proposal only: nothing is removed without the maintainer's go.
- Non-goals: writing any script or hook change; deleting any worktree or branch; model or effort changes.
- Done when:
  - The design names every file a build changes, the new checks with a negative control each, the lane-close truth table, and the ordered build tickets.
  - docs_check.py and check.py pass; no em or en dashes.

## Context
Request from the gen-ui-kit conductor, 2026-10-10: 43 solo lanes and 8 integration branches ended as about 440 worktrees, 887 branches and 24 GB because nothing closed a lane. Same pattern here: .worktrees holds 144 worktrees and 4.4 GB. Asked for 0.22.3 next to plan-campaign; the design cannot make the 0.22.3 cut without delaying it, so it targets 0.22.4 unless the maintainer says otherwise.

## Constraints
Design only. No em or en dashes. No push or publish. Do not remove any worktree or branch.
