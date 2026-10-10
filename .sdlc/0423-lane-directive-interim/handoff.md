---
id: T-0423
title: "Interim written directive: where lanes live, how they open and close, how they are named"
type: chore           # feature | bug | chore | spike | idea
status: ready
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-10
claimed_by: claude 2026-10-10
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The plugin maintenance guidance states where lanes live, how a lane opens and closes, and how branches and worktrees are named, so finished lanes stop piling up.

## Intent
- Do: add one short section "Lanes" to plugins/sdlc-lite/AGENTS.md (and a one-line pointer in the fanout skill and the repo AGENTS.md map only if they already carry a worktree sentence). Content: (1) where: fanout lanes are `<repo>/.worktrees/fanout/<lane>`, sub-agent lanes `.claude/worktrees/`, role temp trees under `$SDLC_TMP_WORKTREES`; all gitignored and excluded from watchers; (2) open: a lane is opened by `fanout.py run` or `prep`, claimed with `claimed_by:`; (3) close: after `fanout.py land` and `tickets.py close`, the lane worktree and branch are removed once their content is on the default branch (ancestor, a MERGED PR whose head sha equals the tip, or every changed file equal); before removal the branch is kept reachable as `refs/archive/<date>/<branch>` and its untracked records are archived; unmerged work is never deleted, locked worktrees (`git worktree lock`) are running lanes and are skipped; (4) names for new work: `lane/<ticket>-<slug>`, `wave/<N>`, `release/<X.Y.Z>`, annotated tags `vX.Y.Z`; existing branches keep their names; (5) until the plugin ships a sweep, the maintainer's tool at `~/.claude/lane/sweep.py` does the removal, dry run by default. Keep it to about 15 lines, one authoritative home, no copied tables.
- Non-goals: any script, hook or check change (T-0422 and T-0424 design that); model or effort changes.
- Done when:
  - The section exists once; `grep -c '^## Lanes' plugins/sdlc-lite/AGENTS.md` prints 1; check.py, docs_check.py and tickets.py check pass; no dashes.

## Context
Maintainer direction 2026-10-10: finished lanes pile up (sdlc-lite 144 worktrees and 4.4 GB, gen-ui-kit 440 and 24 GB). Interim directive approved ("sounds good"); git-native names, archive refs and lock approved with worktree config ("all of it").

## Constraints
No em or en dashes. No push or publish. Do not remove any worktree or branch.
