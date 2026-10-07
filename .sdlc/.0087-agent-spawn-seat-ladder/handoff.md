---
id: T-0087
title: "Seat ladder for conductor Agent-tool spawns outside run.sh, in level-rubric"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
---

## Goal
Agent-tool spawns the conductor makes outside run.sh use a fixed model per seat, never the inherited top model.

## Intent
- Do: add a short "Agent-tool spawns" (seat ladder) section to `plugins/sdlc-lite/skills/level-rubric/SKILL.md` that maps each kind of in-session Agent-tool spawn (one outside run.sh: `general-purpose`, `Explore`, `Plan`, or any spawn naming no agent file) to an explicit `model` by seat class: mechanical or gather-only → `haiku`; search, review, routine coding → `sonnet` (the default); judgment-heavy synthesis → `opus`; never leave `model` unset, because an unset spawn inherits the session's top model. State that a plain Agent spawn cannot set effort, that a `context: fork` / `subagent_type: "fork"` always prices at the parent model and so is never a step-down, and that any work with a run.sh role goes through run.sh, not the Agent tool. Cite the evidence in one line (62 inherited builders at $7.13 each vs $1.82 for an L3 run.sh builder). Add one line to `plugins/sdlc-lite/agents/conductor.md` under "How you run roles" pointing to that section: every Agent-tool spawn states `model` per the level-rubric seat ladder.
- Non-goals: no change to run.sh level tables, to any role's level table in level-rubric, or to the harness plugin; no new hook or lint for spawn models; no copy of harness's full ceiling-ladder prose (fable floors, frontmatter tiers of harness seats).
- Done when: level-rubric has the section and conductor.md has the line, both without em dashes; `plugins/sdlc-lite/scripts/check.sh` passes (the level-table sync between level-rubric, run.sh, and CLAUDE.md still agrees); the CLAUDE.md `skills/level-rubric` layout line and `.claude/agents/sdlc-lite-author.md` are updated only if they describe level-rubric contents that are now stale.

## Context
From peer projects-workspace-optimizer (user's workspace-optimizer session), 2026-09-25: port from harness@nonoun-plugins 3.19.6, which the user keeps disabled at user scope, so sdlc-lite must carry what it needs.

Source: ~/.claude/plugins/cache/nonoun-plugins/harness/3.19.6/skills/agent-writing-rules/SKILL.md, Model tiering section only. Evidence from the peer: a codex-explorations orchestrator spawned 62 general-purpose builders that inherited Opus/Sonnet high and grew to 443k context, at $7.13 each against $1.82 for an L3 run.sh builder. Add a short section to level-rubric and a line to agents/conductor.md.

## Constraints
What must not change. "None" if none.
