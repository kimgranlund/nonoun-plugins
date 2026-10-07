---
id: T-0208
title: "Live evidence: lean and full ticket on both hosts"
type: chore           # feature | bug | chore | spike | idea
status: dropped
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0199, T-0201, T-0207]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Run one lean ticket and one full ticket end to end on Claude and Codex in a throwaway project and record the footprint.

## Intent
- Do: Fixtures: one lean ticket (size M, planner L2, two steps, one swap) and one full ticket (planner L3 or a step at L4). Run each through the conductor on Claude and on Codex. Record `footprint.py` output, role runs, and whether `steps.py lane` chose as expected, with a negative control showing a ticket whose scope names steps.py routes to full. Compare with the Baseline table; state whether the targets (at most 14 files and 60 KB `.md` for a two-step lean ticket) held, and revise the targets in the design if not. Evidence bound to the commit assessed.
- Non-goals: anything outside the files below; changing model or effort defaults; a version bump, tag, push, or publish.
- Done when: the changes listed under Do are built, an independent verifier passed each step, the negative controls named under Do fail before the change and pass after, `bash plugins/sdlc-lite/scripts/check.sh`, `python3 scripts/check-packaging.py`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` and `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` pass, and affected guidance is updated.

## Context
Part of the SDLC Lite design, `docs/specs/sdlc-lite/design.md` (v0.4, build row L16), reviewed twice: `docs/reports/lean-sdlc-design-review.md` and `docs/reports/lean-sdlc-design-review-2.md`. Supersedes part of T-0189 (lean chain), which is closed in favor of these tickets. Depends on: T-0199, T-0201, T-0207. Plan level: L2 (size M). Owning files: docs/reports/lean-sdlc-live-run.md and its evidence folder; no plugin change unless a defect is found (then file it).. Several rows write the same files (steps.py, planner.md, tickets.py, fanout.py); `depends` already sequences them, so never run two of them in parallel lanes. The design was written against main at d4fb850 with `plugins/` unchanged at a7c5685; re-read the cited line numbers before relying on them, they drift. Defaults chosen by the author and changeable by the user: lean thresholds two steps and 12 criteria; migration opt-in; a skip the lane script does not permit needs the user's approval.

## Constraints
Do not substitute offline fixtures for live host validation; if a host cannot run, report unverified. No version bump or release. Follow the root and plugin AGENTS.md invariants: independent verification, model and effort defaults are the user's, no em dashes, keep one authoritative location for each fact. Run roles from the main checkout's run.sh in a separate worktree so a builder never edits a running script.

## Dropped
2026-10-06, by user decision (review of parked tickets): Live lean-vs-full footprint evidence is superseded by docs/reports/solo-vs-lean-benchmark-2026-10-04.md, with live-host evidence now owned by open ticket T-0287; dependencies T-0201 and T-0207 are dropped.

## Deferred (history)
Parked 2026-10-04 by user decision (course correction): the solo-vs-lean evidence showed the default lane is the problem, so tuning the orchestrated chain is frozen until solo has run on real tickets. Revisit with that data. Status blocked, not dropped; handoff otherwise unchanged.
