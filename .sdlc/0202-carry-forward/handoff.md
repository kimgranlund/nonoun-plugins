---
id: T-0202
title: "Carry forward section in scout, researcher, architect, archaeologist"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Add a `## Carry forward` section to the scout, researcher, architect, and archaeologist results and the reader rule to planner and builder.

## Intent
- Do: Each producing role ends its result with `## Carry forward` (at most 15 lines: facts and paths later roles must not re-derive). The planner cites the result path and does not copy it. Planner and builder contracts say to read `## Carry forward` before searching and to search only what it does not answer. A focused live run in a throwaway project shows the planner reading a scout's `## Carry forward` and not repeating the scout's search (compare tool calls with and without). By this design's own mandatory list this is full-chain work.
- Non-goals: anything outside the files below; changing model or effort defaults; a version bump, tag, push, or publish.
- Done when: the changes listed under Do are built, an independent verifier passed each step, the negative controls named under Do fail before the change and pass after, `bash plugins/sdlc-lite/scripts/check.sh`, `python3 scripts/check-packaging.py`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` and `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` pass, and affected guidance is updated.

## Context
Part of the lean SDLC design, `docs/lean-sdlc/design.md` (v0.4, build row L10), reviewed twice: `docs/validation/lean-sdlc-design-review.md` and `docs/validation/lean-sdlc-design-review-2.md`. Supersedes part of T-0191 (single plan record), which is closed in favor of these tickets. Depends on: nothing. Plan level: L3 (size L). Owning files: plugins/sdlc-lite/agents/{scout,researcher,architect,archaeologist}.md, planner.md, builder.md, run.sh required-section handling if affected, check.py guards, regenerated Codex agents, a focused live run.. Several rows write the same files (steps.py, planner.md, tickets.py, fanout.py); `depends` already sequences them, so never run two of them in parallel lanes. The design was written against main at d4fb850 with `plugins/` unchanged at a7c5685; re-read the cited line numbers before relying on them, they drift. Defaults chosen by the author and changeable by the user: lean thresholds two steps and 12 criteria; migration opt-in; a skip the lane script does not permit needs the user's approval.

## Constraints
A role without the section is not a failure of required-section checks for existing results. check.py guards with negative controls. `codex_roles.py generate --check` and the Codex selftest pass. Follow the root and plugin AGENTS.md invariants: independent verification, model and effort defaults are the user's, no em dashes, keep one authoritative location for each fact. Run roles from the main checkout's run.sh in a separate worktree so a builder never edits a running script.
