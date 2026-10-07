---
id: T-0106
title: "Extend .claude/agents/sdlc-lite-author.md line 19 to cover the..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0103
---

## Goal
The sdlc-lite-author invariant on line 19 covers the builder no-Status `rebuild`/`stop` route and the run.sh exit 3 rule, matching CLAUDE.md.

Done: conductor trivial edit to `.claude/agents/sdlc-lite-author.md` line 19; `plugins/sdlc-lite/scripts/check.sh` exit 0 (2026-09-26).

## Context
Follow-up from T-0103 (run-result-format-check/filer-L1.md):

Extend `.claude/agents/sdlc-lite-author.md` line 19 to cover the builder no-Status `rebuild`/`stop` route and run.sh exit 3, so it matches CLAUDE.md.

## Constraints
None.
