---
id: T-0197
title: "steps.py lane, review_required(), and skips.md"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0194]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Add `steps.py lane`, extract `review_required()`, and write the lane and skip history to skips.md.

## Intent
- Do: `steps.py lane <ticket dir>` prints `fix`, `lean`, or `full` on the first line, then `reason:` lines and `read:` lines, like `next` and `review`. Extract `review_required()` from `review_action` (it inlines its reasons near lines 1230-1242) and make `lane` call it, so the two cannot disagree; selftest `(r)` (near 2647) stays green. Decision points: before planning (ticket front matter size only; the front matter has no owner or subsystem field), after the planner result (step levels, merge steps, and the files in each step's scope allow-list parsed with the forms `widen` recognizes, near 1460-1485), and after every append to `## Plan review` (a swap, widen, replan, or review). A lean ticket that meets a mandatory condition becomes `full` from that point. Each call appends its result to the ticket's `skips.md` header. Codex host skill (skills/sdlc-lite/SKILL.md) gains the `steps.py lane` instruction, since it has no steps.py mention today.
- Non-goals: anything outside the files below; changing model or effort defaults; a version bump, tag, push, or publish.
- Done when: the changes listed under Do are built, an independent verifier passed each step, the negative controls named under Do fail before the change and pass after, `bash plugins/sdlc-lite/scripts/check.sh`, `python3 scripts/check-packaging.py`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` and `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` pass, and affected guidance is updated.

## Context
Part of the lean SDLC design, `docs/lean-sdlc/design.md` (v0.4, build row L5), reviewed twice: `docs/validation/lean-sdlc-design-review.md` and `docs/validation/lean-sdlc-design-review-2.md`. Supersedes part of T-0192 (conductor batching), which is closed in favor of these tickets. Depends on: T-0194. Plan level: L3 (size L). Owning files: plugins/sdlc-lite/scripts/steps.py, plugins/sdlc-lite/skills/sdlc-lite/SKILL.md (Codex host skill mention), selftests.. Several rows write the same files (steps.py, planner.md, tickets.py, fanout.py); `depends` already sequences them, so never run two of them in parallel lanes. The design was written against main at d4fb850 with `plugins/` unchanged at a7c5685; re-read the cited line numbers before relying on them, they drift. Defaults chosen by the author and changeable by the user: lean thresholds two steps and 12 criteria; migration opt-in; a skip the lane script does not permit needs the user's approval.

## Constraints
Negative controls: the same two-step plan with one step at L4 gives `full`; a lean ticket whose handoff gains a `## Plan review` line flips to `full` on the next call; before planning, size alone decides. The mandatory list matches steps.py review exactly because it calls the same function. Follow the root and plugin AGENTS.md invariants: independent verification, model and effort defaults are the user's, no em dashes, keep one authoritative location for each fact. Run roles from the main checkout's run.sh in a separate worktree so a builder never edits a running script.
