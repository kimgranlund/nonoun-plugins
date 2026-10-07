---
id: T-0158
title: "Stale running attempt blocks headless Claude runs; .run.lock not ignored"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-28
---

## Goal
A killed run never stops the next headless Claude run in the same handoff dir, and the lock file never lands in a commit.

## Repro
1. SIGKILL the `run_lifecycle.py run` owner (and its process group) during a claude-backend role run.
2. Rerun the same role in that handoff dir: it exits 2 with "Interrupted attempt needs review; run run_lifecycle.py recover".
3. `git status` in a repo that commits `.sdlc/`: `.run.lock` shows as untracked in every handoff dir that ran.

## Expected
- claude exec backend: once `run()` holds the lock, stale `running` records are marked interrupted (as `recover` does) and the run proceeds. That is safe because the child inherits the lock fd through `pass_fds`, so holding the lock proves no owner or child is alive.
- codex subagent transport keeps refusing, because a separately hosted child can outlive the lock.
- `.run.lock` is git-ignored here and in the target-project ignore guidance. Make a stated decision on `*.attempt.json` (kept like runs.jsonl, or ignored).
- Selftest in lifecycle-selftest.py: SIGKILL the owner, and show that the next claude run proceeds while a codex subagent run still refuses. Negative control: without the change the claude case refuses.

## Actual
The next run refuses until someone runs `recover` by hand. Headless conductors (fanout, bench) are not told to, so the lane stops. `.run.lock` is untracked and `git add -A` in fanout lane commits picks it up.

## Context
Raised in docs/other/claude-response.md (items 1 and 2) on Codex commit d4ad342 (0.17.0). Code: plugins/sdlc-lite/scripts/run_lifecycle.py `run()` stale check, `recover()`; docs: skills/handoff-format/run-operations.md.

## Constraints
No change to role, model, or effort mappings. Keep the codex subagent refusal.

## Closed

2026-09-28: Claude exec recovers stale attempts under the directory lock; Codex native still requires explicit recovery; lock files are ignored.
