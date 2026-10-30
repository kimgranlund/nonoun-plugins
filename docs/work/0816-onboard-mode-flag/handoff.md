---
id: T-0816
title: "onboard --mode picks conductor, hybrid or direct"
type: feature        # feature | bug | chore | spike | idea
status: ready        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0815]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-30
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`onboard.py setup --init --mode conductor|hybrid|direct` writes the matching session agent (`sdlc-lite:conductor`, `sdlc-lite:hybrid`, `sdlc-lite:direct`) into `.claude/settings.json` (or `.claude/settings.local.json` with `--local`); the default stays conductor.

## Context
- Design agreed with the user on 2026-10-30 (session reply "sdlc-lite:direct and hybrid modes"): the mode is the choice of Claude Code session agent; scripts, hooks and tickets stay shared. Evidence: plain session $0.82 vs solo plus verifier $2.51 on the same builds, hidden tests 10 of 10 in both (`docs/reports/2026-10-28-speed-experiment.md`).
- T-0813 added the `"agent"` declaration to `plugins/sdlc-lite/scripts/onboard.py` (`settings_change`, `_declare_agent`); an existing `agent` value is kept.
- Skill: `plugins/sdlc-lite/skills/onboard/SKILL.md`; spec: `docs/specs/repo-onboarding/design.md`.

## Do
1. Add `--mode` to setup; it picks the agent value the declaration writes. Unknown values are refused before any write.
2. `check` reports `current <path>` for any of the three sdlc-lite session agents and names the mode.
3. A repo that already names an agent keeps it, as today; print `agent: kept <value> in <path>` and say `--mode` did not apply.
4. Update the skill's Arguments table and the spec row.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/onboard.py selftest` exits 0 with new cases: each mode writes its agent; an unknown mode is refused with nothing written; an existing agent is kept. Each new case fails before the change.
- `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
