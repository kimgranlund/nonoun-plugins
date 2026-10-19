---
id: T-0122
title: "fanout.py inherited_red reads the tests from the newest builder's..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-26
from: T-0114
---

## Goal
When a lane step is `inherited` because the verifier's Verdict is `inherited red: <tests>` (newer than the builder result), fanout.py reports `inherited red: step-<n>: <tests>` with the verifier's tests, not the builder's Status text (e.g. `done`). A builder-inherited step keeps reporting the builder's tests.

## Context
Follow-up from T-0114 (verifier-fail-on-a-gate/filer-L1.md):

fanout.py `inherited_red()` reads the tests from the newest builder's `## Status`, so a verifier-inherited step reports `inherited red: step-<n>: done` and names the wrong tests; read them from the verifier Verdict when that is newer.

## Constraints
Only `plugins/sdlc-lite/scripts/fanout.py` (inherited_red, its docstrings, and its selftest) changes, plus any record describing this behavior (CLAUDE.md fanout bullet, `.claude/agents/sdlc-lite-author.md`, skills/fanout) if it names the builder-only source. Use `steps.py`/`order.py` for which result is newest; never mtime. `scripts/check.sh` stays green. Never commit.
