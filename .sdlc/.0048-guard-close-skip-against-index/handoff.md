---
id: T-0048
title: "Guard close --skip against index drift: if the filer file changes..."
type: idea            # feature | bug | chore | spike | idea
status: done
size: M              # S | M | L | XL
priority: P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
from: T-0041
---

## Goal
`tickets.py close <slug> --skip N[,N...]` never skips the wrong follow-ups: if the filer file's Follow-ups list changed after the `--dry-run` that produced the indices, close refuses and writes nothing instead of applying stale indices.

Done when: a dry run prints a token that identifies the exact follow-up list it indexed; `close --skip` checks it against the current list and refuses on a mismatch (stderr names the drift, nothing written); /file (skills/file/SKILL.md step 3) passes the token through; the selftest proves the guard bites (edit the filer file between dry run and --skip → refusal, unchanged → close succeeds); CLAUDE.md's tickets.py line and the usage/docstring describe it; `scripts/check.sh` passes.
(gap: mechanism not specified; default: dry run prints a short content digest of the ordered follow-up titles, `close` takes `--expect <digest>`, and `--skip` without `--expect` refuses. Planner may pick an equivalent mechanism if it states why.)

## Context
Follow-up from T-0041 (confirm-follow-ups/filer-L1.md):

Guard `close --skip` against index drift: if the filer file changes between `--dry-run` and `--skip`, the indices shift and the wrong follow-ups get skipped (no lock or content check today).

## Constraints
- Python stdlib only; keep existing close, --dry-run, --reason, --force, --numbered behavior and existing selftest cases passing.
- Plain `close <slug>` with no --skip needs no token (nothing index-based to drift).
- Refusals follow the existing style: Fail with a message ending in "nothing written", exit 1.
- Files in scope: plugins/sdlc-lite/scripts/tickets.py, plugins/sdlc-lite/skills/file/SKILL.md, plugins/sdlc-lite/skills/ticket/SKILL.md, CLAUDE.md (repo root). The author agent (.claude/agents/sdlc-lite-author.md) requires close --dry-run/--skip to stay in sync across all four.

## Triage
2026-09-24, user-approved: keep, P3; guard --skip against filer-file drift between dry run and close.
