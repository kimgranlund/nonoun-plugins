---
id: T-0201
title: "Anchor rule for step blocks and its lint check"
type: feature        # feature | bug | chore | spike | idea
status: blocked     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0200]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Add the anchor rule: step blocks cite settled decisions by anchor instead of restating them, with a lint check.

## Intent
- Do: Design section 2 change 2. `steps.py split` adds only the goal to a step block (near line 897), so the restatement is planner-written: a step block holds the criteria, scope, `### Read first`, and `### Do`, and cites a settled decision as `plan: <planner file>#<anchor>`. `steps.py lint` resolves each anchor against the plan file named in the same step block and refuses a dangling one. Measure before and after on a fixture with `footprint.py` (T-0193).
- Non-goals: anything outside the files below; changing model or effort defaults; a version bump, tag, push, or publish.
- Done when: the changes listed under Do are built, an independent verifier passed each step, the negative controls named under Do fail before the change and pass after, `bash plugins/sdlc-lite/scripts/check.sh`, `python3 scripts/check-packaging.py`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` and `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` pass, and affected guidance is updated.

## Context
Part of the lean SDLC design, `docs/lean-sdlc/design.md` (v0.4, build row L9), reviewed twice: `docs/reports/lean-sdlc-design-review.md` and `docs/reports/lean-sdlc-design-review-2.md`. Supersedes part of T-0191 (single plan record), which is closed in favor of these tickets. Depends on: T-0200. Plan level: L2 (size M). Owning files: plugins/sdlc-lite/agents/planner.md, plugins/sdlc-lite/scripts/steps.py (`lint`), selftests, regenerated Codex agents.. Several rows write the same files (steps.py, planner.md, tickets.py, fanout.py); `depends` already sequences them, so never run two of them in parallel lanes. The design was written against main at d4fb850 with `plugins/` unchanged at a7c5685; re-read the cited line numbers before relying on them, they drift. Defaults chosen by the author and changeable by the user: lean thresholds two steps and 12 criteria; migration opt-in; a skip the lane script does not permit needs the user's approval.

## Constraints
Existing plans without anchors still lint and split. Negative control: a step block with a dangling anchor fails lint. Follow the root and plugin AGENTS.md invariants: independent verification, model and effort defaults are the user's, no em dashes, keep one authoritative location for each fact. Run roles from the main checkout's run.sh in a separate worktree so a builder never edits a running script.

## Deferred
Parked 2026-10-04 by user decision (course correction): the solo-vs-lean evidence showed the default lane is the problem, so tuning the orchestrated chain is frozen until solo has run on real tickets. Revisit with that data. Status blocked, not dropped; handoff otherwise unchanged.
