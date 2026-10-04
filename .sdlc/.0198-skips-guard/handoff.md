---
id: T-0198
title: "skips.md guard in tickets.py check and close"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0197]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Add a skips.md guard to tickets.py check and close, exempting tickets closed before the feature.

## Intent
- Do: A closed ticket whose recorded lane is `lean` or `fix` must hold a `skips.md` entry (one line: role, step, reason, who decided) for every role the full chain would have run. The guard lives in tickets.py, not check.py, because check.py checks plugin contracts and never runs in a consumer repo. Tickets closed before the feature (no `skips.md`, closed before the guard's introduction marker) are exempt, so `check` does not go red on upgrade or on the 190+ existing tickets. Selftest positive; negative controls: a lean ticket missing a required entry fails `check`; a pre-feature closed ticket without skips.md passes.
- Non-goals: anything outside the files below; changing model or effort defaults; a version bump, tag, push, or publish.
- Done when: the changes listed under Do are built, an independent verifier passed each step, the negative controls named under Do fail before the change and pass after, `bash plugins/sdlc-lite/scripts/check.sh`, `python3 scripts/check-packaging.py`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` and `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` pass, and affected guidance is updated.

## Context
Part of the lean SDLC design, `docs/lean-sdlc/design.md` (v0.4, build row L6), reviewed twice: `docs/validation/lean-sdlc-design-review.md` and `docs/validation/lean-sdlc-design-review-2.md`. Supersedes part of T-0192 (conductor batching), which is closed in favor of these tickets. Depends on: T-0197. Plan level: L2 (size M). Owning files: plugins/sdlc-lite/scripts/tickets.py (check near 1508-1514, close near 1300) and its selftest.. Several rows write the same files (steps.py, planner.md, tickets.py, fanout.py); `depends` already sequences them, so never run two of them in parallel lanes. The design was written against main at d4fb850 with `plugins/` unchanged at a7c5685; re-read the cited line numbers before relying on them, they drift. Defaults chosen by the author and changeable by the user: lean thresholds two steps and 12 criteria; migration opt-in; a skip the lane script does not permit needs the user's approval.

## Constraints
Preserve cross-worktree id uniqueness, reference-safe closure, and the explicit follow-up selection. Do not change `close`'s existing refusal rules. Follow the root and plugin AGENTS.md invariants: independent verification, model and effort defaults are the user's, no em dashes, keep one authoritative location for each fact. Run roles from the main checkout's run.sh in a separate worktree so a builder never edits a running script.

## Burn-down brief
Standing frame: done is better than perfect; trust capable models given useful context. Make the smallest change that meets the Intent. One or two steps, builder L3 at most unless a step truly needs L4. No per-ticket live run: rely on selftests, checks and the branch verifier, and record a flaky or missing live arm as a known limit. Scope is frozen: a new requirement becomes a new ticket. Report blocked instead of looping.
