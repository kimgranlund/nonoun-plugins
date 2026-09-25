---
id: T-0087
title: "Seat ladder for conductor Agent-tool spawns outside run.sh, in level-rubric"
type: feature        # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
---

## Goal
Agent-tool spawns the conductor makes outside run.sh use a fixed model per seat, never the inherited top model.

## Intent
- Do:
- Non-goals:
- Done when:

## Context
From peer projects-workspace-optimizer (user's workspace-optimizer session), 2026-09-25: port from harness@nonoun-plugins 3.19.6, which the user keeps disabled at user scope, so sdlc-lite must carry what it needs.

Source: ~/.claude/plugins/cache/nonoun-plugins/harness/3.19.6/skills/agent-writing-rules/SKILL.md, Model tiering section only. Evidence from the peer: a codex-explorations orchestrator spawned 62 general-purpose builders that inherited Opus/Sonnet high and grew to 443k context, at $7.13 each against $1.82 for an L3 run.sh builder. Add a short section to level-rubric and a line to agents/conductor.md.

## Constraints
What must not change. "None" if none.
