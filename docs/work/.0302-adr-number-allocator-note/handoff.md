---
id: T-0302
title: "ADR number allocator note (repo-owned, docs only)"
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A short repo-owned note (docs only) on allocating ADR numbers so two sibling worktrees never take the same one.

## Context
Idea only, no build. Source: agent-ui root-cause 2026-10-06 section 2: T-0012 and T-0014 both took ADR-0235 in sibling worktrees, found by a plan reviewer by luck. The allocator is the consumer repo's to own; sdlc-lite adds only a docs note (for example in handoff-format or onboard), not code.

## Acceptance criteria
- `grep -q '^## Numbered records across worktrees (ADR numbers)' plugins/sdlc-lite/skills/handoff-format/SKILL.md`
- `awk '/^## Numbered records across worktrees/{f=1;next} /^## /{f=0} f' plugins/sdlc-lite/skills/handoff-format/SKILL.md | grep -q 'git worktree list'`
- `! git diff --name-only HEAD | grep -v -E '^(\.sdlc/0302-adr-number-allocator-note/handoff\.md|plugins/sdlc-lite/skills/handoff-format/SKILL\.md|plugins/sdlc-lite/adapters/codex/agents/sdlc-planner-l[123]\.toml)$' | grep -q .`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 plugins/sdlc-lite/scripts/check.py`
- `python3 scripts/check-packaging.py`
- `git diff --check`

## Closed

2026-10-06: delivered by the solo agent (tier M); one independent batched verifier passed before the merge
