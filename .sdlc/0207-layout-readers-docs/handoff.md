---
id: T-0207
title: "Readers and docs for the topic layout"
type: chore           # feature | bug | chore | spike | idea
status: proposed
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0206]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Update board.py, statusline.sh, traces, and docs and skills paths for the topic layout.

## Intent
- Do: Resolve paths through the resolver. board.py already reads `ticket_root` (near line 213) and traces/ingest.py and traces/sources/tickets.py:20 do too; extend to roadmap and notes. Update the live docs and skills that name the old paths, listing each in the result; never rewrite dated validation records. Selftests on a topics-layout fixture for board, statusline, and traces.
- Non-goals: anything outside the files below; changing model or effort defaults; a version bump, tag, push, or publish.
- Done when: the changes listed under Do are built, an independent verifier passed each step, the negative controls named under Do fail before the change and pass after, `bash plugins/sdlc-lite/scripts/check.sh`, `python3 scripts/check-packaging.py`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` and `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` pass, and affected guidance is updated.

## Context
Part of the SDLC Lite design, `docs/sdlc-lite/design.md` (v0.4, build row L15), reviewed twice: `docs/reports/lean-sdlc-design-review.md` and `docs/reports/lean-sdlc-design-review-2.md`. Supersedes part of T-0190 (topic sub-folders), which is closed in favor of these tickets. Depends on: T-0206. Plan level: L2 (size M). Owning files: plugins/sdlc-lite/scripts/board.py, plugins/sdlc-lite/scripts/statusline.sh, plugins/sdlc-lite/scripts/traces/sources/tickets.py (line 28 hardcodes notes.md), skills and docs that print `.sdlc/roadmap.md` or `.sdlc/notes.md` (not dated docs/reports records), check.py:330 message string.. Several rows write the same files (steps.py, planner.md, tickets.py, fanout.py); `depends` already sequences them, so never run two of them in parallel lanes. The design was written against main at d4fb850 with `plugins/` unchanged at a7c5685; re-read the cited line numbers before relying on them, they drift. Defaults chosen by the author and changeable by the user: lean thresholds two steps and 12 criteria; migration opt-in; a skip the lane script does not permit needs the user's approval.

## Constraints
Flat layout output unchanged. check.py:330 matches the suffix `/step-1/handoff.md` only, so only its message string changes. Follow the root and plugin AGENTS.md invariants: independent verification, model and effort defaults are the user's, no em dashes, keep one authoritative location for each fact. Run roles from the main checkout's run.sh in a separate worktree so a builder never edits a running script.

## Dropped (history, reinstated below)
2026-10-06, by user decision (review of parked tickets): Readers for a layout dropped with T-0205. See docs/reports/parked-tickets-review-2026-10-06.md.

## Deferred (history)
Parked 2026-10-04 by user decision (course correction): the solo-vs-lean evidence showed the default lane is the problem, so tuning the orchestrated chain is frozen until solo has run on real tickets. Revisit with that data. Status blocked, not dropped; handoff otherwise unchanged.

## Reinstated
2026-10-06, by user decision ("we should still do T-206"): the topic layout (T-0205 resolver, T-0206 migration, T-0207 readers and docs) is back as a unit, since T-0206 depends on T-0205 and the layout is useless without its readers. The earlier drop reason (numbered folders plus `tickets.py archive` cover the clutter) is recorded in docs/reports/parked-tickets-review-2026-10-06.md. Re-plan against the current design (docs/sdlc-lite/design.md v0.4, build row L14, docs schema T-0240 to T-0243, the sub-agent mode) before building; the docs/ versus .sdlc/ boundary rules in docs/docs-schema/design.md apply. Size L: use the lane script, a full chain only with the stated reason (L-size plan).
