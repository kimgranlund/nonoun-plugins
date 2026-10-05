---
id: T-0194
title: "Lean lane text and coarse-step rule in chain and planner"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Add the lean lane text and the coarse-step rule to the chain skill and the planner contract, plus a steps.py lint warning, so a size-S or M ticket can run in one or two coarse steps.

## Intent
- Do: Section 'Lean chain' of the design: lean conditions (planner L1 or L2, at most two steps each at builder L1 to L3, no merge step, no replan, one nearest AGENTS.md owner or one script and its tests, no change to a contract other roles parse), the full-chain mandatory list, the coarse-step rule ('one step per independently verifiable outcome', up to 12 criteria per step, merge adjacent same-level sequential steps, whole-suite gates stay on the final `gates green` step), and the lean close-out that always runs the filer (resolved decision 2). `steps.py lint` warns, never refuses, when a lean-eligible plan has more than two steps or a step with one criterion. No `steps.py lane` yet: that is T-0197. Text must not claim a lane the code cannot compute.
- Non-goals: anything outside the files below; changing model or effort defaults; a version bump, tag, push, or publish.
- Done when: the changes listed under Do are built, an independent verifier passed each step, the negative controls named under Do fail before the change and pass after, `bash plugins/sdlc-lite/scripts/check.sh`, `python3 scripts/check-packaging.py`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` and `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` pass, and affected guidance is updated.

## Context
Part of the lean SDLC design, `docs/lean-sdlc/design.md` (v0.4, build row L2), reviewed twice: `docs/reports/lean-sdlc-design-review.md` and `docs/reports/lean-sdlc-design-review-2.md`. Supersedes part of T-0189 (lean chain), which is closed in favor of these tickets. Depends on: nothing. Plan level: L2 (size M). Owning files: plugins/sdlc-lite/skills/chain/SKILL.md, plugins/sdlc-lite/agents/planner.md, plugins/sdlc-lite/scripts/steps.py (lint warning only), plugins/sdlc-lite/scripts/check.py guards, regenerated Codex agents (`codex_roles.py generate`).. Several rows write the same files (steps.py, planner.md, tickets.py, fanout.py); `depends` already sequences them, so never run two of them in parallel lanes. The design was written against main at d4fb850 with `plugins/` unchanged at a7c5685; re-read the cited line numbers before relying on them, they drift. Defaults chosen by the author and changeable by the user: lean thresholds two steps and 12 criteria; migration opt-in; a skip the lane script does not permit needs the user's approval.

## Constraints
Do not loosen the mandatory list: planner L3, any step at L4 or L5, any merge step, any replan, a `## Plan review` line, an `unresolved:` assumption keep the full chain and plan review. Selftest `(r)` in steps.py stays green. A check.py guard with a negative control for the new text. Codex generate --check passes. Follow the root and plugin AGENTS.md invariants: independent verification, model and effort defaults are the user's, no em dashes, keep one authoritative location for each fact. Run roles from the main checkout's run.sh in a separate worktree so a builder never edits a running script.
