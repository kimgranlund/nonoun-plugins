---
id: T-0223
title: "/agent command: launch an SDLC Lite agent by name on instructions"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`/sdlc-lite:agent {agent-name} {instructions}` launches the named SDLC Lite agent on the instructions, in the background, through the start path that agent's kind requires, and reports the result path and a short summary.

## Intent
- Do: add skills/agent/SKILL.md mapping the name to its start path (solo through the agents/solo.md Bash start at the tier's model and effort; scout, researcher, architect, archaeologist through scripts/run.sh with a handoff the skill writes from the instructions; every other sdlc-lite agent name answered with a pointer to its existing skill, conductor refused, unknown names answered with the valid list), print the lane and tier in one line first, follow the interactive vs headless rule in agents/conductor.md and never use the Agent tool for an sdlc-lite: agent from a conductor; add a check.py guard (item 25) that the skill's valid-name list agrees with agents/*.md and the Codex mapping, with a negative control; add the skill to the skill listings the repo keeps.
- Non-goals: creating new agent definitions; agents outside SDLC Lite; model or effort changes; a version bump, tag, push, or publish.
- Done when: the skill, guard and listing exist; an independent verifier passed; a live run on Claude Code shows /agent scout returning a result, /agent solo delivering a change that passes a hidden check, and an unknown name and conductor refused; docs/validation/agent-command-live-run.md records it with committed evidence.

## Context
User request 2026-10-05: "add command for creating sub-agents /agent {agent-name} {instructions}". User answers: launch an existing agent (not author a new one), SDLC Lite agents only. Size M, lane solo (burn-down rules), one handwritten builder step, one independent verifier.

## Constraints
Keep the skill short. One authoritative location per fact: the start paths live in agents/solo.md and the role skills; the new skill points to them. No em dashes.
