---
id: T-0749
title: "One owner-tree rule and helper for sdlc records"
type: chore           # feature | bug | chore | spike | idea
status: ready     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-24
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
One documented rule says which checkout owns each kind of sdlc state, and one helper answers it, so later tickets can route every script through it.

## Intent
- Do: derive the rule from current behaviour (do not change it) and write one table in `docs/references/sdlc-internals.md`: kind of state, owning tree, who writes, who reads. Cover at least verifier and builder records (records dir), base-sha and end-sha, `.sdlc/config` keys (merge_gate, light_scope), ticket bookkeeping (branch:, worktree:, roadmap, router) and lane-close state. Add one helper in `plugins/sdlc-lite/scripts/` (for example `wtroot.owner_tree(kind, ticket, cwd)`, or a small new module) that returns the owning tree for a kind, plus a selftest with one case per kind across primary, integration and lane worktrees. No caller changes here.
- Non-goals: routing the scripts through it (T-0750 to T-0752); new features; changing what is recorded.
- Done when: the criteria pass.

## Context
Split from T-0734 (root-cause review 2026-10-22): 8 issues share one cause, the tools span three checkouts (primary, integration, lane worktree) and each script picks its own: #46/#57 (lane close writes main, land merges integration), #55 (prepare --tree writes main, land reads lane), #58 (config on integration, land reads main), #59 (closed folder on integration, open copy in lane), #49 (build base vs lane start), #47 (end tree before a review fix). Each fix so far added a fallback. Settled behaviour to keep: T-0713, T-0717, T-0720, T-0722, T-0723, T-0740, T-0744, T-0745, T-0747, T-0748.

## Acceptance criteria
1. The rule table exists in `docs/references/sdlc-internals.md`, names the helper, and has a row for each kind listed in Intent.
2. The helper's selftest has one case per kind (primary, integration and lane trees built in a throwaway repo), and a deliberately wrong mapping makes at least one case fail (state the FAIL line).
3. The helper's selftest passes, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.
