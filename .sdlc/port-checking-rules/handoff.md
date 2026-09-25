---
id: T-0084
title: "Port harness checking-rules into sdlc-lite; add to verifier skills"
type: feature        # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
---

## Goal
The verifier applies review discipline: evidence to dismiss, run rather than trust a claim, steelman before filing.

## Intent
- Do:
- Non-goals:
- Done when:

## Context
From peer projects-workspace-optimizer (user's workspace-optimizer session), 2026-09-25: port from harness@nonoun-plugins 3.19.6, which the user keeps disabled at user scope, so sdlc-lite must carry what it needs.

Source: ~/.claude/plugins/cache/nonoun-plugins/harness/3.19.6/skills/checking-rules/SKILL.md (131 lines). Add as a plugin skill (trimmed, sdlc-lite wording) and list it in agents/verifier.md `skills:` next to checks-that-bite; run.sh appends declared skills. Matters more now that verifier L2 runs on Sonnet high (0.8.3).

## Constraints
What must not change. "None" if none.
