---
id: T-0492
title: "Merge ops duty block in conductor.md, fanout skill steps 4 and 5, and a recipe in run-operations.md (T-0488)"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0489]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The conductor owns merge operations as a short duty block, backed by scripts: enqueue, dequeue, status and what never to do, so no lane or tree is left for a later hand sweep.

## Intent
- Do: add a `## Merge ops` block of about eight lines to `plugins/sdlc-lite/agents/conductor.md` (enqueue is `fanout.py land <branch>` as a background Bash call; dequeue after the user picks it is `fanout.py settle <integration> --forward` then `lanes.py sweep --apply`; status is `board.py --lanes` plus `lanes.py list --stale`; a land gate runs at `--priority 1`; release cutting stays the maintainer's through AskUserQuestion; never push, tag, publish, delete an unmerged branch, or move main except by fast-forward); rewrite fanout `SKILL.md` steps 4 and 5 to call the same scripts; add a `Merge ops` recipe to `skills/handoff-format/run-operations.md`; add the new terms to `check.py`'s agreement sets (`:10`, `:30-37`). Regenerate with `claude_roles.py generate` and `codex_roles.py generate`.
- Non-goals: a new role or session agent; any model or effort row; prompt wording beyond this block (the controlled-language pass T-0461 owns style).
- Done when: `claude_roles.py generate --check`, `codex_roles.py generate --check`, `check.py` and `prompt_lint.py` exit 0 with `conductor.md` prohibitions not above its current count; a `check.py` case fails when the conductor, the fanout skill and `run-operations.md` disagree on the settle command (observed red).

## Context
Design: `docs/planning/merge-ops-and-queue.md` (Approach 4, 5). Depends on T-0489 for the `--forward` flag it names.

## Constraints
Affirmative wording, one rule per line; no new prohibition beyond the Never line. One writer on `conductor.md`.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check` exits 0.
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` exits 0.
- `python3 plugins/sdlc-lite/scripts/check.py` exits 0, and its merge ops case fails when `run-operations.md` carries a different settle command than the conductor (observed red with `settle <integration> --forward` replaced by `settle <integration>` there).
- `python3 plugins/sdlc-lite/scripts/prompt_lint.py` exits 0 and reports `agents/conductor.md: prohibitions 30` (not above its count before the change).
- `git diff --check` exits 0.

## Closed

2026-10-12: delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full
