---
id: T-0206
title: "tickets.py migrate-layout"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0205]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Add `tickets.py migrate-layout [--dry-run] [--rewrite-refs]` for flat to topics migration.

## Intent
- Do: Design section 3 migration. Refuse on a dirty tree (id uniqueness is not a precondition: each worktree resolves its own root). Move ticket folders into `tickets/`, task folders without a ticket into `work/`, `roadmap.md` to `tickets/`, `notes.md` to `notes/`. Run the existing citing-file scan (outside_refs near 510-535) for every moved ticket folder, plus a new cite scan for `roadmap.md` and `notes.md`; refuse naming each citing file, or rewrite them with `--rewrite-refs`. Never rewrite dated records under docs/validation/. Write both `ticket_root: tickets` and `layout: topics`, regenerate router and roadmap, run `check`. Idempotent: a second run moves nothing. `--dry-run` lists every move and rewrite and writes nothing. Selftest on a fixture repo with cites; negative controls: dirty tree refused; unrewritten cite reported; stray root folder fails check after migration is skipped.
- Non-goals: anything outside the files below; changing model or effort defaults; a version bump, tag, push, or publish.
- Done when: the changes listed under Do are built, an independent verifier passed each step, the negative controls named under Do fail before the change and pass after, `bash plugins/sdlc-lite/scripts/check.sh`, `python3 scripts/check-packaging.py`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` and `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` pass, and affected guidance is updated.

## Context
Part of the lean SDLC design, `docs/lean-sdlc/design.md` (v0.4, build row L14), reviewed twice: `docs/validation/lean-sdlc-design-review.md` and `docs/validation/lean-sdlc-design-review-2.md`. Supersedes part of T-0190 (topic sub-folders), which is closed in favor of these tickets. Depends on: T-0205. Plan level: L3 (size L). Owning files: plugins/sdlc-lite/scripts/tickets.py, selftest, docs/maintenance/sdlc-internals.md, upgrade note.. Several rows write the same files (steps.py, planner.md, tickets.py, fanout.py); `depends` already sequences them, so never run two of them in parallel lanes. The design was written against main at d4fb850 with `plugins/` unchanged at a7c5685; re-read the cited line numbers before relying on them, they drift. Defaults chosen by the author and changeable by the user: lean thresholds two steps and 12 criteria; migration opt-in; a skip the lane script does not permit needs the user's approval.

## Constraints
Do not run migration on this repository inside this ticket's build; use fixtures. Preserve ids and references. Follow the root and plugin AGENTS.md invariants: independent verification, model and effort defaults are the user's, no em dashes, keep one authoritative location for each fact. Run roles from the main checkout's run.sh in a separate worktree so a builder never edits a running script.
