---
id: T-0816
title: "onboard --mode picks conductor, hybrid or direct"
type: feature        # feature | bug | chore | spike | idea
status: done        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0815, T-0819]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-30
claimed_by: sdlc-lite-author 2026-10-30
branch: lane/T-0816-t0816
worktree: ../sdlc-lite.worktrees/T-0816-t0816
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`onboard.py setup --init --mode factory|hybrid|live` writes the matching session agent (`sdlc:factory`, `sdlc:hybrid`, `sdlc:live`) into `.claude/settings.json` (or `.claude/settings.local.json` with `--local`); the default stays conductor.

## Context
- Names follow T-0819 (plugin `sdlc`, agents `sdlc:factory`, `sdlc:hybrid`, `sdlc:live`); build on the renamed tree.
- Design agreed with the user on 2026-10-30 (session reply "sdlc:live and hybrid modes"): the mode is the choice of Claude Code session agent; scripts, hooks and tickets stay shared. Evidence: plain session $0.82 vs solo plus verifier $2.51 on the same builds, hidden tests 10 of 10 in both (`docs/reports/2026-10-28-speed-experiment.md`).
- T-0813 added the `"agent"` declaration to `plugins/sdlc/scripts/onboard.py` (`settings_change`, `_declare_agent`); an existing `agent` value is kept.
- Skill: `plugins/sdlc/skills/onboard/SKILL.md`; spec: `docs/specs/repo-onboarding/design.md`.

## Do
1. Add `--mode` to setup; it picks the agent value the declaration writes. Unknown values are refused before any write.
2. `check` reports `current <path>` for any of the three sdlc-lite session agents and names the mode.
3. A repo that already names an agent keeps it, as today; print `agent: kept <value> in <path>` and say `--mode` did not apply.
4. Update the skill's Arguments table and the spec row.

## Acceptance criteria
- `python3 plugins/sdlc/scripts/onboard.py selftest` exits 0 with new cases: each mode writes its agent; an unknown mode is refused with nothing written; an existing agent is kept. Each new case fails before the change.
- `python3 plugins/sdlc/scripts/check.py` exits 0.

## Outcome

2026-10-30 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full) · verifier: verifier-L2 (sonnet) · base: 1de29b3b3083
- Changed: see commits
- Commits: bb61515 T-0816: onboard --mode picks factory, hybrid or live; 589bdaa T-0816: record lane T-0816-t0816
- Check: 1 `python3 plugins/sdlc/scripts/onboard.py selftest` exits 0 with new cases (each mode writes its a...: pass
- Check: 2 `python3 plugins/sdlc/scripts/check.py` exits 0: pass
- Follow-up: decide: plugins/sdlc/scripts/onboard.py:76: the handoff Goal says "default... -> notes.md
- Follow-up: decide: Red-first order was not separately replayed; redck.py deviations... -> notes.md
