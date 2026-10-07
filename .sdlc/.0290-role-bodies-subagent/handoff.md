---
id: T-0290
title: "Role bodies optimized for session and sub-agent execution"
type: chore           # feature | bug | chore | spike | idea
status: done        # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Rewrite the shared role bodies (scout, researcher, architect, archaeologist, planner, plan-reviewer, builder, verifier, filer, solo) so each runs well as a session agent or a named background sub-agent, while the headless run.sh path keeps working.

## Intent
- Do: add an input contract (blocked with the exact question), an output contract (compact final message in the results.py shape, optional result file checked with `results.py validate --role`), resume behavior, numeric stop rules, commit and worktree boundary, cost discipline, and a routing description; drop run.sh wording. Regenerate the Codex agents.
- Non-goals: conductor.md and messenger.md; any model or effort value; check.py contracts; new scripts.
- Done when: check.py, codex_roles.py generate --check, check-packaging.py, tickets.py check, and git diff --check are green; one solo ticket and one verifier run live through run.sh in a /tmp throwaway; a record at docs/reports/role-bodies-subagent.md; one verifier (L3) passes.

## Context
Design: docs/lean-sdlc/subagent-mode.md on branch worktree-agent-a8796067dca9eb594 (read-only). Sub-agent definitions will embed these bodies per level, so bodies stay level-neutral.

## Constraints
Preserve every phrase and section check.py and results.py assert. No push, publish, tag, or merge into main.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/check.py` exits 0
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` exits 0
- `python3 scripts/check-packaging.py` exits 0
- `for r in scout researcher architect archaeologist planner plan-reviewer builder verifier filer solo; do grep -q "results.py" plugins/sdlc-lite/agents/$r.md || exit 1; done`
- `! grep -l "run\.sh" plugins/sdlc-lite/agents/scout.md plugins/sdlc-lite/agents/researcher.md plugins/sdlc-lite/agents/architect.md plugins/sdlc-lite/agents/archaeologist.md plugins/sdlc-lite/agents/builder.md plugins/sdlc-lite/agents/verifier.md plugins/sdlc-lite/agents/filer.md plugins/sdlc-lite/agents/plan-reviewer.md`
- `git diff --quiet main -- plugins/sdlc-lite/agents/conductor.md plugins/sdlc-lite/agents/messenger.md plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/adapters/codex/models.json`
- `test -s docs/reports/role-bodies-subagent.md`

## Closed

2026-10-06: Role bodies rewritten; checks green; verifier L3 pass after one fix. Record docs/reports/role-bodies-subagent.md
