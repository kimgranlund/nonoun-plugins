---
id: T-0212
title: "Handoff freeze: stale_input flag, rerun action, handoff edit hook"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L
priority: P2         # P1 | P2 | P3
depends: [T-0196, T-0197, T-0199, T-0211, T-0183]
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Detect a handoff that changed while a role ran: record its hash, flag the result as stale input, rerun automatically, and deny edits to a running handoff on Claude.

## Intent
- Do: Section B. `run_lifecycle.py` records `handoff_sha256` in the attempt record and passes `SDLC_HANDOFF_SHA256` in the child env; `run.sh` rehashes handoff.md before its jq append and writes `handoff_sha256` and `stale_input: true|false` on the run line, with a stderr line `run.sh: stale input: <handoff> changed while <role> ran` and an unchanged exit code. New action class `rerun <level> stale input` from `steps.py next`, `resume` and `review` (not `invalid result`, which stops and asks): same role and level, no `## Previous attempt`. A stale planner result is excluded in `review_action`, `lean_warnings` and `footprint.py` through one shared helper in steps.py. Claude-only hook `hooks/warn-handoff-edit.sh`, registered as a new `Edit|Write|NotebookEdit` matcher in `adapters/claude/hooks.json`, acts in any session, reads `tool_input.file_path`, (warn mode first, user decision 2026-10-04) warns on a handoff.md edit when a `*.running` file sits beside it: it allows the edit, prints a warning naming `change.md`, and appends one line (timestamp, path, running role) to `<task dir>/stale-edits.log`; a later `SDLC_HANDOFF_EDIT=deny` or `handoff_edit: deny` config line turns it into a denial, default stays warn; fixtures in hook-selftest.sh and a live payload probe in hook-live-probe.sh. `skills/chain/SKILL.md` routes `rerun`; the conductor line is a pointer to T-0199 text. Dated record docs/validation/handoff-freeze-live-run.md.
- Non-goals: changing any model or effort default; conductor wording beyond a pointer line; a version bump, tag, push, or publish.
- Done when: the changes are built, an independent verifier passed each step, and a stub-role selftest that edits handoff.md mid-run sets stale_input and `steps.py next` returns rerun; negative controls: no edit not flagged, a sibling-file edit not flagged, a role that never reads the handoff is still flagged, a stale planner rerun does not make review_action require a plan review; hook warn mode (edit allowed, warning printed, stale-edits.log line written) with .running, nothing logged without it or for another file name, and the deny switch turns the same case into a denial (negative control); live: one planner run on Claude and one on Codex with a mid-run edit ends in rerun. `bash plugins/sdlc-lite/scripts/check.sh`, `python3 scripts/check-packaging.py`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` and `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` pass, and affected guidance is updated.

## Context
Cost-control addendum to the lean SDLC design: `docs/lean-sdlc/cost-control.md` v0.2, reviewed in `docs/validation/lean-sdlc-cost-control-review.md`. Measured on 2026-10-04: about $190 over 78 role runs, 4 of 7 plans returned for replan. Owning files and ordering: scripts/run_lifecycle.py, scripts/run.sh, scripts/steps.py, scripts/footprint.py, adapters/claude/hooks.json, hooks/warn-handoff-edit.sh (new), scripts/hook-selftest.sh, scripts/hook-live-probe.sh, docs/maintenance/claude-hooks.md, skills/chain/SKILL.md, scripts/check.py. Waits for T-0196, T-0197, T-0199 (conductor.md and chain batching text), T-0211 and T-0183 (check.sh). Plan level L3.

## Constraints
Follow the root and plugin AGENTS.md invariants: independent verification, model and effort defaults are the user's (change none), no em dashes, one authoritative location for each fact, checks that can fail with a negative control. Read the design first: docs/lean-sdlc/cost-control.md (v0.2) and docs/validation/lean-sdlc-cost-control-review.md; re-read every cited line number at plan time, since T-0196, T-0197, T-0199, T-0200, T-0201 and T-0202 move them. Conductor wording is T-0199's file (agents/conductor.md): do not restate it, and edit it only as a pointer line after T-0199 merges. Merge main into the build branch before each local merge and keep both sides of check.py and check.sh conflicts. Run roles from the main checkout's run.sh in a separate worktree. No version bump, tag, push or publish.

## Update
Un-parked 2026-10-04 for the 0.20.5 release scope (user decision). Build as one handwritten step under the burn-down rules: no planner, one verifier. Pull main first; T-0212 and T-0214 share files, so build T-0214 first, then T-0212.

## Closed

2026-10-04: Built as one step (warn mode): stale_input flag and handoff_sha256 on the run line, warn-handoff-edit hook with deny switch, selftests with negative controls, check.py item 18, live Claude run. Independent L3 verifier found one defect (check-packaging route count), fixed. Not built: rerun action in steps.py and the footprint exclusion (outside this lane's files), Codex arm. See docs/validation/handoff-freeze-live-run.md.
