---
id: T-0148
title: "Conductor scope decisions update the acceptance criteria, not just prose"
type: feature        # feature | bug | chore | spike | idea
status: done        # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-28
---

## Goal
A conductor decision that widens a step's scope edits the scope guard the criteria read, so the next builder does not block on the old guard.

## Intent
Literal ask: Conductor scope decisions update the acceptance criteria, not just prose. A conductor decision that widens a step's scope edits the scope guard the criteria read, so the next builder does not block on the old guard.
Deltas:
- Where the conductor records a scope decision: gap: the originating lane logs live in another repo; default: the decision reaches the step through the step handoff (a `## Previous attempt` note, a `## Plan review` entry, or an answer the conductor writes after a builder block), while the step's scope criterion (a `git diff --name-only "$SDLC_BASE_SHA"` allow-list, see agents/planner.md rule 6) is left unchanged, so the builder obeys the old guard and blocks.
- Mechanism: defaulted: the conductor never hand-edits a criterion (chain item 8: "never edit the criterion by hand"); a widening decision goes through a script-checked path that rewrites the scope criterion (extend `steps.py` with a scope-widen action, or route it through the existing planner L3 replan / `steps.py swap` path), whichever the planner judges smallest and consistent with "whoever writes the work never sets its check".
- Which docs: defaulted: the conductor contract (agents/conductor or equivalent session guidance), skills/chain/SKILL.md, and any role/rubric text that states the rule; generated Codex agents regenerated through scripts/codex_roles.py if their source changes.
Do: Make a conductor scope-widening decision update the step's scope-guard criterion through a checked path, and state the rule in the conductor and /chain contracts so prose-only widening is not the documented route.
Non-goals: Narrowing scope; changing how the planner writes scope guards at plan time; changes to other repos.
Done when: A documented, script-checked route exists by which a conductor scope decision rewrites the step's scope-guard criterion; a regression check shows that after the route runs, the widened file passes the step's scope criterion and a file outside the widened set still fails it (negative control); chain/conductor docs name the route; `bash plugins/sdlc-lite/scripts/check.sh` passes.

## Context
From the gen-ui-system-svelte-lite overnight run 2026-09-28, feedback batch 3 item 1 (peer setup-sdlc-lite-generative-ui). Evidence is in that repo's lane logs.
## Constraints
What must not change. "None" if none.
