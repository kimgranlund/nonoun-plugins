---
id: T-0064
title: "Merge-step conflict-marker guard scans the whole tree when git diff..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0059
---

## Goal
The merge-step template's conflict-marker guard criterion never scans the whole tree: when `git diff --name-only HEAD^1 HEAD` lists no paths, the check passes (nothing merged, nothing to scan) instead of running `git grep` with no pathspec, and it still fails when a touched file holds a real conflict marker line.

## Context
Follow-up from T-0059 (merge-step-template/filer-L1.md):

Merge-step conflict-marker guard scans the whole tree when `git diff --name-only HEAD^1 HEAD` is empty and can flag legitimate lines starting with seven `<` or `>`; make it fail safe or skip on an empty path list.

## Constraints
- The template lives in two copies, `plugins/sdlc-lite/agents/planner.md` (`## Merge steps`) and `plugins/sdlc-lite/skills/handoff-format/SKILL.md`; `plugins/sdlc-lite/scripts/check.py` keeps them identical, lint-clean (`bash -n` on criterion spans, as `steps.py lint`), and in step with `agents/builder.md`. Change both copies together and keep `scripts/check.sh` green.
- The criterion stays one command span that parses under `bash -n`, keeps its `(guard)` tag, and keeps the other four criteria unchanged.
- Paths with spaces or odd characters in the touched-file list must not break the check (prefer `-z`/NUL-safe or `git diff`-driven forms over word splitting).
- Any doc that restates the criterion (CLAUDE.md Decisions "no conflict markers in touched files", `.claude/agents/sdlc-lite-author.md`, builder.md, verifier.md) stays accurate; update records in the same change if wording changes.
- No commit, push, or publish.
