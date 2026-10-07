---
id: T-0049
title: "Newest result is picked by mtime, which checkout resets"
type: bug             # feature | bug | chore | spike | idea
status: done
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
---

## Goal
Which result is newest (builder, verifier, planner) is decided from recorded run order, so a fresh clone or a committed .sdlc/ trail reads the same verdicts as the machine that ran them.

## Repro
1. Exact command or steps, from a clean checkout.

## Expected

## Actual
Paste the output or error verbatim.

## Context
Review 2026-09-24: git checkout gives every file the same mtime. In a fresh worktree, bench-summary reported button-geometry as 2/3 steps passed (it picked step-2's older failing verifier-L1.attempt2.md among equal mtimes); on the original checkout it reports 3/3. The same mtime rule decides the newest file in board.py (by_level, the verifier-after-build check), bench-summary.sh, and run.sh's verifier model swap (`ls -t builder-L*`). runs.jsonl already records run order per dir (ts, role, level); since T-0038, reruns are named <role>-<level>-<k>. Suggested: derive "newest" from runs.jsonl order (fall back to name order), never mtime, with a selftest that sets equal mtimes.

## Constraints
The failing test lands before or with the fix, never after.

## Conductor notes (scouted 2026-09-24)
Every "newest file" decision that uses mtime today (all paths under plugins/sdlc-lite/scripts/):
- board.py:51 `by_level` sorts role files by st_mtime; board.py:93 verifier-after-build compares mtimes. (board.py:167 and the task-dir sort at 246-260 order task folders by recency for display; they are not verdict decisions and may stay mtime.)
- bench-summary.sh:22 picks the verifier with `-nt`.
- run.sh:60 picks the last builder with `ls -t builder-L*.md` for the verifier model swap.
- steps.py:40 picks the newest planner by mtime (its selftest case (c) asserts mtime order).
- tickets.py:465 picks the newest filer by mtime (selftest (h) asserts mtime order).
runs.jsonl sits next to each handoff (run.sh writes one line per run: ts, role, level, and the result file). Check what run.sh actually writes before relying on a field. Prefer one shared ordering rule (runs.jsonl order, fallback: level then rerun index -k, name order) implemented once and reused where practical; shell callers may call a python helper. Every changed selftest must set equal mtimes and prove the order does not come from mtime. scripts/check.sh must pass at the end. Update CLAUDE.md, .claude/agents/sdlc-lite-author.md and any skill text that says "by mtime" for these decisions.
