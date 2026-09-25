---
id: T-0086
title: "Close-out sweep at the end of /chain: batch unresolved items into one AskUserQuestion round"
type: feature        # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
---

## Goal
A /chain run ends with one batched AskUserQuestion round for everything left unresolved.

## Intent
- Do:
- Non-goals:
- Done when:

## Context
From peer projects-workspace-optimizer (user's workspace-optimizer session), 2026-09-25: port from harness@nonoun-plugins 3.19.6, which the user keeps disabled at user scope, so sdlc-lite must carry what it needs.

Source: ~/.claude/plugins/cache/nonoun-plugins/harness/3.19.6/skills/find-open-questions/SKILL.md (76 lines). The conductor asks per decision but has no close-out sweep. Unattended runs list the items in the report instead.

## Constraints
What must not change. "None" if none.
