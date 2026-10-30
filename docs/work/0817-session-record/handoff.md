---
id: T-0817
title: "One sessions.jsonl row per session so retros compare modes"
type: feature        # feature | bug | chore | spike | idea
status: claimed        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0815, T-0819]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-30
claimed_by: sdlc-lite-author 2026-10-30
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Each Claude Code session in a repo using SDLC Lite leaves one row in `.sdlc/runtime/sessions.jsonl` (mode, start and end time, estimated cost, commits made, test commands run), and `fleet_collect.py` reports spend and commits per mode, so a retro can compare factory, hybrid and live on real work.

## Context
- Names follow T-0819 (plugin `sdlc`, agents `sdlc:factory`, `sdlc:hybrid`, `sdlc:live`); build on the renamed tree.
- Design agreed with the user on 2026-10-30 (session reply "sdlc:live and hybrid modes"): the mode is the choice of Claude Code session agent; scripts, hooks and tickets stay shared. Evidence: plain session $0.82 vs solo plus verifier $2.51 on the same builds, hidden tests 10 of 10 in both (`docs/reports/2026-10-28-speed-experiment.md`).
- Direct-mode sessions write no `runs.jsonl`, so today a retro would see nothing for them.
- Cost from a transcript: `cost_estimate.estimate(transcript_model(t), transcript_usage(t))`; hook registration: `plugins/sdlc/hooks/hooks.json` and `docs/references/claude-hooks.md`.

## Do
1. A session-end hook (Claude Code `SessionEnd`, or `Stop` if SessionEnd is unavailable; state which and why) runs a small script that appends one row: `mode` (the session agent type or `none`), `session_id`, `started_at`, `ended_at`, `cost_usd`, `commits` (count on the current branch between start and end), `checks` (count of Bash calls that ran a test or check command, best effort). Never fails the session: on any error it writes nothing and exits 0.
2. `fleet_collect.py` adds `sessions: {by_mode: {<mode>: {count, cost_usd, commits}}}` to the fingerprint.
3. Document the row in `docs/references/sdlc-internals.md`.

## Acceptance criteria
- The new script's selftest exits 0 with a fixture transcript producing one row, and an unreadable transcript producing none with exit 0.
- `python3 plugins/sdlc/scripts/fleet_collect.py selftest` exits 0 with a case aggregating two modes. Each new case fails before the change.
- `python3 plugins/sdlc/scripts/check.py` exits 0 and `python3 scripts/check-packaging.py` exits 0.

## Constraints
- Claude Code only; Codex gets no hook and no row, stated in the reference.
