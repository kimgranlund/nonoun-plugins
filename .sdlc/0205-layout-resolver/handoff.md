---
id: T-0205
title: "layout key and one resolver for ticket dir, roadmap, notes"
type: feature        # feature | bug | chore | spike | idea
status: blocked     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0204]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Add the `layout` config key and one resolver for ticket dir, roadmap path, and notes path, plus stray checks and onboard variants.

## Intent
- Do: Design section 3. `layout: topics|flat` beside `ticket_root` (which stays explicit because other worktrees and branches resolve trees by their own `ticket_root`). One function returns ticket dir, roadmap path (`tickets/roadmap.md` under topics), and notes path (`notes/notes.md`); every caller that builds `root / 'roadmap.md'` or `root / 'notes.md'` (near tickets.py:842, 851, 1231, 1308, 1547, 1595) uses it, as do the citing-file scan skip (near 535) and the router template text (near 894). `check` fails on stray root content once `layout: topics` is set and warns (exit 0) on a flat repo naming `migrate-layout`. `write_roadmap` also regenerates `messages/AGENTS.md`, so this ticket owns that text. onboard.py renders the managed block from resolved paths: a flat repo's block text and TEMPLATE_VERSION are unchanged (a bump marks every existing block stale), a topics repo renders the topics variant. Selftests: both layouts; negative controls for strays and for a flat repo staying `current` under `onboard.py check`.
- Non-goals: anything outside the files below; changing model or effort defaults; a version bump, tag, push, or publish.
- Done when: the changes listed under Do are built, an independent verifier passed each step, the negative controls named under Do fail before the change and pass after, `bash plugins/sdlc-lite/scripts/check.sh`, `python3 scripts/check-packaging.py`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` and `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` pass, and affected guidance is updated.

## Context
Part of the lean SDLC design, `docs/lean-sdlc/design.md` (v0.4, build row L13), reviewed twice: `docs/reports/lean-sdlc-design-review.md` and `docs/reports/lean-sdlc-design-review-2.md`. Supersedes part of T-0190 (topic sub-folders), which is closed in favor of these tickets. Depends on: T-0204. Plan level: L3 (size L). Owning files: plugins/sdlc-lite/scripts/tickets.py, plugins/sdlc-lite/scripts/onboard.py, plugins/sdlc-lite/scripts/check.py guards, messages.py entry-file text owned by write_roadmap.. Several rows write the same files (steps.py, planner.md, tickets.py, fanout.py); `depends` already sequences them, so never run two of them in parallel lanes. The design was written against main at d4fb850 with `plugins/` unchanged at a7c5685; re-read the cited line numbers before relying on them, they drift. Defaults chosen by the author and changeable by the user: lean thresholds two steps and 12 criteria; migration opt-in; a skip the lane script does not permit needs the user's approval.

## Constraints
Default stays flat for existing repos; new repos get topics. Preserve cross-worktree id uniqueness and reference-safe closure. Build only after the fanout resolver lands. Follow the root and plugin AGENTS.md invariants: independent verification, model and effort defaults are the user's, no em dashes, keep one authoritative location for each fact. Run roles from the main checkout's run.sh in a separate worktree so a builder never edits a running script.

## Deferred
Parked 2026-10-04 by user decision (course correction): the solo-vs-lean evidence showed the default lane is the problem, so tuning the orchestrated chain is frozen until solo has run on real tickets. Revisit with that data. Status blocked, not dropped; handoff otherwise unchanged.
